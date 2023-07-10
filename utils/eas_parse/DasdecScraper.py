""" Playwright scraper class for DASDEC """
from typing import Optional, Tuple
from bs4 import BeautifulSoup
from playwright._impl._api_types import TimeoutError

class DasdecScraper:
    def __init__(self, playwright, **kwargs):
        self.url = f"http://{kwargs['ip_addr']}/dasdec/dasdec.csp"
        self.username = kwargs["username"]
        self.password = kwargs["password"]
        self.name = kwargs["name"]
        self.timeframe = kwargs["timeframe"] if kwargs.get("timeframe") else '2weeks'
        self.get_logs = True if kwargs.get("get_logs") == True else False
        self.playwright = playwright
        self.page = None    
        self.context = None
        self.browser = None
        
    async def scrape(self) -> Tuple[int, str]:
        """ Scraping automation """
        await self._initialize_browser()

        # attempt login to unit, alert on incorrect creds or no connection
        response_code, content = await self._login()

        if response_code == 200:
            # nav to correct tabs
            await self._navigate_to_proper_page()

            if self.get_logs:
                content = await self._get_content_from_txt_log()
            else:
                content = await self.page.content()

        # close playwright context
        await self.context.close()
        await self.browser.close()

        return response_code, content
    

    async def _initialize_browser(self):
        """ Create browser context and embedded http_creds """
        self.browser = await self.playwright.chromium.launch()
        self.context = await self.browser.new_context(http_credentials={
            'username': self.username,
            'password': self.password
        })
        self.page = await self.context.new_page()


    async def _login(self) -> Tuple[int, str]:
        """ Login logic """
        response = (200, 'success')
        try:
            await self._load_login_page()
            await self._fill_credentials()
        except TimeoutError:
            response = (500, 'No response from unit, please check network connectivity')
        except ValueError as e:
            response = (403, e)
        except:
            response = (400, 'An unknown error occurred')
        finally:
            return response

    async def _load_login_page(self) -> None:
        """ Nav to login page """
        await self.page.goto(self.url, timeout=3000)
        await self.page.wait_for_load_state('networkidle')
        return

    async def _fill_credentials(self) -> None:
        """ Use passed creds to login """
        await self.page.fill('input[name=login_user]', self.username)
        await self.page.fill('input[name=login_password]', self.password)
        await self.page.click('input[name=Login]')
        await self.page.wait_for_load_state('networkidle')
        content = await self.page.content()
        if "Login failed" in content:
            raise ValueError('Login failed, please check your credentials')
        return

    async def _navigate_to_proper_page(self) -> None:
        """ Trigger page events to reach the proper tab """
        await self._nav_to_alert_events_tab()
        await self._nav_to_all_alerts_submenu()
        await self._select_time_frame()
        return

    async def _nav_to_alert_events_tab(self) -> None:
        """ Evaluate JS to navigate to the proper tab if not already there """
        content = await self.page.content()
        if not self._proper_tab_selected(content):
            await self.page.evaluate('''() => {
                select_page_level(document.forms[0], '0', decoder_page, '', '0');
            }''')
            await self.page.wait_for_selector('body')
        return

    def _proper_tab_selected(self, content: str) -> bool:
        """ Check if Alert Events tab is selected """
        soup = BeautifulSoup(content, 'lxml')
        menu_tabs = soup.find_all('td', class_="mainmenu_unseltab")
        for tab in menu_tabs:
            if tab.text.strip() == 'Alert Events':
                return False
        return True

    async def _nav_to_all_alerts_submenu(self) -> None:
        """ Click to select All Alerts if not already checked """
        submenu_selector = 'input[type="radio"][name="DecoderSubmenu"][value="All"]'
        submenu_button = await self.page.query_selector(submenu_selector)

        if not await submenu_button.evaluate('element => element.checked'):
            await self.page.click(submenu_selector)
            await self.page.wait_for_selector('body')
        return

    async def _select_time_frame(self) -> None:
        """ Find log timeframe and select the desired timeframe, default 7 days """
        select_element = await self.page.query_selector('select[name="AlertRange"]')
        if select_element:
            selected_option_value = await select_element.evaluate('element => element.value')
            if selected_option_value != self.timeframe:
                await self.page.select_option('select[name="AlertRange"]', value=self.timeframe)
                await self.page.wait_for_selector('body')
        return

    async def _get_content_from_txt_log(self) -> str:
        """ Generates txt log, """
        link = await self._get_txt_log_link()
        if not link:
            content = 'Error: download link not found'
        else:
            await self.page.click(link)
            await self.page.wait_for_timeout(1000)

            # txt file opens in a new tab. gather content of the new tab
            context_pages = self.context.pages
            new_page = context_pages[-1]
            content = await new_page.inner_text('body pre')
        return content

    async def _get_txt_log_link(self) -> Optional[str]:
        """ Report # incremented each time a new log is created. Find current """
        for i in range(0, 10):
            link = await self.page.query_selector(f'a[href="/dasdec_originated_events/report{i}.txt"]')
            if link:
                return f'a[href="/dasdec_originated_events/report{i}.txt"]'
        return None

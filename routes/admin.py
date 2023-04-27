"""
Create routes for Admin page to edit config
"""
import os

# -----IMPORTS-----
from flask import abort, Blueprint, current_app, flash, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User, Site, Channel, MeterConfig, StatusOption
from marshmallow import ValidationError


# create Blueprint object
admin = Blueprint('admin', __name__)


# -----ROUTES-----
@admin.route('/home')
def home():
    """ Admin homepage """
    sites = Site.query.order_by(Site.site_order.asc()).all()
    operators = User.query.all()

    return render_template('admin/home.html', sites=sites, operators=operators)


# ----- USER CONFIG -----
@admin.route('/add_user')
def add_new_user():
    """ Route to Add User """
    return render_template('admin/add_user.html')


@admin.route('/add_user', methods=['POST'])
def add_new_user_post():
    """ On Submit, Post data to database """
    results = request.form

    try:
        # get results
        first_name = results['first_name'].replace(' ', '').lower().title()
        last_name = results['last_name'].replace(' ', '').lower().title()
        name = f'{first_name}*{last_name}'
        username = results['username']
        password = generate_password_hash(results.get('password'), method='sha256')
        privilege = results.get('privilege')

        query_name = User.query.filter_by(name=name).first()
        if query_name:
            raise ValidationError('User of that name already exists in database')

        new_user = User(
            name=name,
            username=username,
            password=password,
            privilege=privilege
        )
        db.session.add(new_user)
        db.session.commit()
        flash_message = f'User: {name.replace("*", " ")} added successfully'
    except ValidationError as err:
        flash_message = err
    except Exception as e:
        current_app.logger.warning(e)
        flash_message = e
    flash(flash_message)
    return redirect(url_for('admin.home'))


@admin.route('user/<int:user_id>/update')
def update_user(user_id):
    """ Load user data at index if exists """
    user = User.query.get_or_404(user_id)
    return render_template('admin/update_user.html', user=user)


@admin.route('user/<int:user_id>/update', methods=['POST'])
def update_user_post(user_id):
    # gather data
    user = User.query.get(user_id)
    results = request.form

    try:
        first_name = results.get('first_name').replace(' ', '').lower().title()
        last_name = results.get('last_name').replace(' ', '').lower().title()

        name = f'{first_name}*{last_name}'
        password = generate_password_hash(results.get('password'), method="sha256")
        privilege = results.get('privilege')
        username = results.get('username')

        user.name = name
        user.password = password
        user.username = username
        user.privilege = privilege

        db.session.commit()
        flash('User successfully updated', 'success')
    except Exception as e:
        current_app.logger.info(e)
        flash('Error updating user', 'error')

    return redirect(url_for('admin.update_user', user_id=user_id))


@admin.route('user/<int:user_id>/delete')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/delete_user.html', user=user)


@admin.route('user/<int:user_id>/delete', methods=["POST"])
def delete_user_post(user_id):
    # TODO: Make sure deletion doesn't ruin the reading query
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)  # Delete the user
        db.session.commit()  # Commit the changes to the database session
        flash('User deleted successfully', 'success')
    except Exception as e:
        current_app.logger.info(e)
        flash('User deletion failed', 'error')
    return redirect(url_for('admin.home'))


# ----- SITE CONFIG -----
@admin.route('/add_site')
def add_new_site():
    """ Render page for adding a new site """
    return render_template('admin/add_site.html')


@admin.route('/add_site', methods=['POST'])
def add_new_site_post():
    """ On POST, attempt to add site to config """
    # Get form data from post
    results = request.form

    try:
        site_name = results.get('site_name').replace(' ', '_')

        # Encrypt API KEY
        from extensions.encryption import encrypt_api_key
        encrypted_api_key = encrypt_api_key(results['api_key'])

        # Add site to database
        site = Site(
            site_name=site_name,
            ip_addr=results.get('ip'),
            api_key=encrypted_api_key
        )

        # Construct site data
        # TODO: Have channels be added adhoc
        from routes.api import get_setup_channels
        setup_channels = get_setup_channels(results)

        meter_configs, status_options = create_channel_model_data(setup_channels, results, site.id)

        db.session.add(site)
        db.session.add_all(meter_configs)
        db.session.add_all(status_options)
        db.session.commit()

        flash_message = f"Site: {site_name} added successfully!"
    except Exception as e:
        current_app.logger.info(e)
        flash_message = str(e)
    flash(flash_message)
    return redirect(url_for('admin.home'))


@admin.route('site/<int:site_id>/update_site')
def update_site(site_id):
    """ Load site data if site in config """
    site = Site.query.get_or_404(site_id)
    return render_template('admin/update_site.html', site=site)


@admin.route('site/<int:site_id>/update_site', methods=['POST'])
def update_site_post(site_id):
    """ Updates config of site if  """
    # Gather form results and current config data
    site = Site.query.get_or_404(site_id)
    results = request.form

    try:
        site.site_name = results.get('site_name')
        site.ip_addr = results.get('ip')
        if results.get('api_key'):
            from extensions.encryption import encrypt_api_key
            site.api_key = encrypt_api_key(results.get('api_key'))

        db.session.commit()
        flash_message = 'Site updated'
    except Exception as e:
        db.session.rollback()
        current_app.logger.info(e)
        flash_message = 'Something went wrong with update'
    flash(flash_message)
    return redirect(url_for('admin.update_site', site_id=site_id))


@admin.route('site/<int:site_id>/update_channels')
def update_channels(site_id):
    site = Site.query.get_or_404(site_id)

    from routes.api import get_colors, get_units
    colors = get_colors()
    units = get_units()

    return render_template('admin/update_channels.html', site=site, colors=colors, units=units)


@admin.route('site/<int:site_id>/update_channels', methods=['POST'])
def update_channels_post(site_id):
    channels = Channel.query.filter_by(site_id=site_id).all()
    results = request.form

    # TODO: Make functional

    for channel in channels:
        print(channel.title)
        if channel.html_tag in results.keys():
            print(channel.html_tag)
    return results


@admin.route('site/<int:site_id>/delete')
def delete_site(site_id):
    site = Site.query.get_or_404(site_id)
    return render_template('admin/delete_site.html', site=site)


@admin.route('site/<int:site_id>/delete', methods=["POST"])
def delete_site_post(site_id):
    """ Delete all items associated with the site """
    site_to_delete = Site.query.get_or_404(site_id)
    site_name = site_to_delete.site_name

    # Remove API KEY from YAML
    config_data = load_yaml()
    del config_data[f'{site_name}_API_KEY']
    update_yaml(config_data)

    channels = Channel.query.filter_by(site_id=site_id).all()
    for channel in channels:
        # delete meter configs associated with channel
        meter_config_to_del = MeterConfig.query.filter_by(channel_id=channel.id).all()
        for config in meter_config_to_del:
            db.session.delete(config)

        # delete status options associated with channel
        status_opt_to_del = StatusOption.query.filter_by(channel_id=channel.id).all()
        for option in status_opt_to_del:
            db.session.delete(option)
        db.session.delete(channel)
    db.session.delete(site_to_delete)
    db.session.commit()

    flash(f'{site_name} removed and associated channel data')
    return redirect(url_for('admin.home'))


def create_channel_model_data(input_channels, results, site_id):
    """
    Given form data, input_channels, and a target site
    Return channels associated to the site with correct config objects
    """
    meter_configs = []
    status_options = []
    for chan in input_channels:
        html_tag = chan['html_tag']
        channel = Channel(
            chan_type=chan['type'],
            title=chan['title'],
            site_id=site_id
        )
        db.session.add(channel)
        target_channel = Channel.query.filter_by(title=chan['title'], site_id=site_id).first()
        if channel.chan_type == 'meter':
            config = MeterConfig(
                units=results[f'{html_tag}_units'],
                burk_channel=int(results[f'{html_tag}_num']),
                nominal_output=float(results[f'{html_tag}_nominal']),
                upper_limit=float(results[f'{html_tag}_upper']),
                upper_lim_color=results.get(f'{html_tag}_upper_color'),
                lower_limit=float(results[f'{html_tag}_lower']),
                lower_lim_color=results.get(f'{html_tag}_lower_color'),
                channel_id=target_channel.id,
            )
            meter_configs.append(config)
        if channel.chan_type == 'status':
            from routes.api import get_options
            options = get_options(html_tag, results)
            for option in options:
                status_opt = StatusOption(
                    burk_channel=option['burk_channel'],
                    selected_value=option['selected_value'],
                    selected_state=option['selected_state'],
                    selected_color=option['selected_color'],
                    channel_id=target_channel.id,
                )
                status_options.append(status_opt)
    return meter_configs, status_options


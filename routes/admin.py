"""
Create routes for Admin page to edit config
"""
import os

# -----IMPORTS-----
from flask import abort, Blueprint, current_app, flash, jsonify, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User, Site, Channel, MeterConfig, StatusOption
from models.schemas import SiteSchema, UserSchema, UserCreationSchema
from marshmallow import ValidationError


# create Blueprint object
admin = Blueprint('admin', __name__)


# -----ROUTES-----
@admin.route('/home')
@login_required
def home():
    """ Admin homepage """
    if not current_user.is_admin:
        abort(403)
    else:
        site_schema = SiteSchema(many=True)
        sites = Site.query.order_by(Site.site_order.asc()).all()
        site_data = site_schema.dump(sites)

        user_schema = UserSchema(many=True)
        users = User.query.order_by(User.last_name).all()
        user_data = user_schema.dump(users)

        return render_template('admin/admin_home.html', sites=site_data, operators=user_data)


# ----- USER CONFIG -----
@admin.route('/add_user')
@login_required
def add_new_user():
    """ Route to Add User """
    if not current_user.is_admin:
        abort(403)
    else:
        return render_template('admin/add_user.html')


@admin.route('/add_user', methods=['POST'])
@login_required
def add_new_user_post():
    """ On Submit, Post data to database """
    form_data = request.form

    try:
        add_user_schema = UserCreationSchema()      # password hashed in creation
        new_user = add_user_schema.load_user(form_data)

        # privilege can be user, admin, or both.
        privilege = int(form_data.get('privilege'))
        new_user.is_admin = True if privilege in [2, 3] else False
        new_user.is_operator = True if privilege in [1, 3] else False

        db.session.add(new_user)
        db.session.commit()
        flash_message = f'User: {new_user.name} added successfully'
    except ValidationError as err:
        flash_message = err
    except Exception as e:
        current_app.logger.warning(e)
        flash_message = e
    flash(flash_message)
    return redirect(url_for('admin.home'))


@admin.route('user/<int:user_id>/update')
@login_required
def update_user(user_id):
    """ Load user data at index if exists """
    if not current_user.is_admin:
        abort(403)
    else:
        user_schema = UserSchema()
        user_obj = User.query.get_or_404(user_id)
        user = user_schema.dump(user_obj)

        return render_template('admin/update_user.html', user=user)


@admin.route('user/<int:user_id>/update', methods=['POST'])
@login_required
def update_user_post(user_id):
    # gather data
    user = User.query.get(user_id)
    results = request.form

    try:
        # TODO: Create UPDATE SCHEMA
        first_name = results.get('first_name').replace(' ', '').lower().title()
        last_name = results.get('last_name').replace(' ', '').lower().title()

        password = generate_password_hash(results.get('password'), method="scrypt")
        privilege = int(results.get('privilege'))
        username = results.get('username')

        user.first_name = first_name
        user.last_name = last_name
        user.password = password
        user.username = username
        user.is_admin = True if privilege in [2,3] else False
        user.is_operator = True if privilege in [1,3] else False

        db.session.commit()
        flash(f'User {user.name} successfully updated', 'success')
    except Exception as e:
        current_app.logger.info(e)
        flash('Error updating user', 'error')

    return redirect(url_for('admin.update_user', user_id=user_id))


@admin.route('user/<int:user_id>/delete')
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)
    else:
        user = User.query.get_or_404(user_id)
        try:
            name = user.name
            db.session.delete(user)  # Delete the user
            db.session.commit()  # Commit the changes to the database session
            flash(f'User ({name}) deleted successfully', 'success')
        except Exception as e:
            current_app.logger.info(e)
            flash(f'User ({name}) deletion failed', 'error')
        return redirect(url_for('admin.home'))


# ----- SITE CONFIG -----
@admin.route('/add_site')
@login_required
def add_new_site():
    """ Render page for adding a new site """
    if not current_user.is_admin:
        abort(403)
    else:
        return render_template('admin/add_site.html')


@admin.route('/add_site', methods=['POST'])
@login_required
def add_new_site_post():
    """ On POST, attempt to add site to config """
    # Get form data from post
    results = request.form
    try:
        # TODO: Create Site Creation Schema
        site_name = results.get('site_name').replace(' ', '_')

        # Encrypt API KEY
        from extensions.encryption import encrypt_api_key
        encrypted_api_key = encrypt_api_key(results['api_key'])

        # Add site to database
        site = Site(
            site_name=site_name,
            ip_addr=results.get('ip_addr'),
            api_key=encrypted_api_key
        )

        db.session.add(site)
        db.session.commit()

        target_site = Site.query.filter_by(site_name=site_name).first()

        # Create channel data and add to database
        from extensions.channel_CRUD import sort_results_channel_data, create_new_channels
        channel_data = sort_results_channel_data(results)[1]    # returns tuple, new_channel data is at index 1
        create_new_channels(channel_data, target_site.id)

        flash_message = f"Site: {site_name} added successfully!"
    except Exception as e:
        current_app.logger.info(e)
        flash_message = str(e)
    flash(flash_message)
    return redirect(url_for('admin.home'))


@admin.route('site/<int:site_id>/update_site')
@login_required
def update_site(site_id):
    """ Load site data if site in config """
    if not current_user.is_admin:
        abort(403)
    else:
        from extensions.encryption import decrypt_api_key
        site = Site.query.get_or_404(site_id)
        site_schema = SiteSchema()
        site_data = site_schema.dump(site)
        site_data['api_key'] = decrypt_api_key(site.api_key)

        return render_template('admin/update_site.html', site=site_data)


@admin.route('site/<int:site_id>/update_site', methods=['POST'])
@login_required
def update_site_post(site_id):
    """ Updates config of site if  """
    # Gather form results and current config data
    site = Site.query.get_or_404(site_id)
    results = request.form

    try:
        site_name = results.get('site_name').replace(' ', '_')
        obj_w_site_name = Site.query.filter_by(site_name=site_name).first()
        if obj_w_site_name and obj_w_site_name != site:
            raise ValidationError('Conflict in the database. Site of that name already exists.')

        site.site_name = site_name
        site.ip_addr = results.get('ip_addr')

        from extensions.encryption import encrypt_api_key
        site.api_key = encrypt_api_key(results.get('api_key'))

        db.session.commit()
        flash_message = 'Site updated', 'success'
    except ValidationError as err:
        db.session.rollback()
        current_app.logger.info(err)
        flash_message = err.messages, 'error'
    flash(flash_message)
    return redirect(url_for('admin.update_site', site_id=site_id))


@admin.route('site/<int:site_id>/update_channels')
@login_required
def update_channels(site_id):
    """ Update channel for a specific site"""
    if not current_user.is_admin:
        abort(403)
    else:
        site = Site.query.get_or_404(site_id)
        site_schema = SiteSchema()
        site_data = site_schema.dump(site)

        from routes.api import get_colors, get_units
        colors = get_colors()
        units = get_units()

        return render_template('admin/update_channels.html', site=site_data, colors=colors, units=units)


@admin.route('site/<int:site_id>/update_channels', methods=['POST'])
@login_required
def update_channels_post(site_id):
    results = request.form

    from extensions.channel_CRUD import handle_channel_update
    handle_channel_update(results, site_id)

    flash(f'Channels for site {(Site.query.get(site_id)).site_name} have been updated')
    return redirect(url_for('admin.home'))


@admin.route('site/<int:site_id>/delete')
@login_required
def delete_site(site_id):
    """ Delete site and associated channels from database """
    if not current_user.is_admin:
        abort(403)
    else:
        site_to_delete = Site.query.get_or_404(site_id)
        site_name = site_to_delete.site_name

        from extensions.channel_CRUD import delete_channel
        for channel in site_to_delete.channels:
            delete_channel(channel.id)
        db.session.delete(site_to_delete)
        db.session.commit()

        flash(f'{site_name} removed and associated channel data')
        return redirect(url_for('admin.home'))

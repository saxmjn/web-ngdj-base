from datetime import timedelta
import json
import logging
# DJANGO
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
# PROJECT
from app import constants
from app.utils import validate_get_phone, raise_error, validate_email, validate_phone, get_phone_or_null
from user.models import UserProfile


AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")

logger = logging.getLogger('application')


class UserContactsImport(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, db_index=True, on_delete=models.CASCADE)
    phone_import_recorded = models.BooleanField(default=False)

    @classmethod
    def check_phone_record(cls, user):
        try:
            data = cls.objects.get(user=user)
            return data.phone_import_recorded
        except ObjectDoesNotExist:
            return None


class UserContact(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, db_index=True, on_delete=models.CASCADE)
    contact = models.ForeignKey(AUTH_USER_MODEL, null=True, related_name="user_contact", on_delete=models.CASCADE)
    source = models.CharField(max_length=10, choices=constants.imported_contact_sources_choices)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True, db_index=True, null=True)
    phone_code = models.CharField(max_length=5, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    state = models.CharField(max_length=10, choices=constants.user_contact_states_choices, default='0')
    block_invites = models.BooleanField(default=False)
    registered = models.BooleanField(default=False)
    invited_at = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        get_latest_by = "created"
        ordering = ['-created']
        verbose_name = "User Contacts"

    @staticmethod
    def get_from_email(user, email, fail_silently=True):
        """
        Look for contact by email
        :param user:
        :param email:
        :param fail_silently:
        :return:
        """
        if email:
            try:
                query_ = UserContact.objects.filter(user=user, email__iexact=email)
                return query_.first()
            except ObjectDoesNotExist:
                if fail_silently:
                    return None
                else:
                    raise raise_error('ERR-CONT-001')



    @staticmethod
    def get_from_phone(user, phone, fail_silently=True):
        """
        Look for contact by phone
        :param user:
        :param phone:
        :param fail_silently:
        :return:
        """
        phone_data = validate_get_phone(phone)
        if phone:
            try:
                query = UserContact.objects.filter(user=user, phone_number=phone_data['phone_number'],
                                                   phone_code=phone_data['phone_code'])
                return query.first()
            except ObjectDoesNotExist:
                if fail_silently:
                    return None
                else:
                    raise raise_error('ERR-CONT-002')

    def action_if_contact_on_tc(self, email, phone):
        """
        Checks for contact as a TapChief user and updates the state & contact field
        :param self:
        :param email:
        :param phone:
        :return:
        """
        # find user from email
        user_from_email = User.objects.filter(email=email).first()
        # find user from phone
        user_from_phone = UserProfile.match_user_from_phone(phone=phone)
        # If user is found for contact, then update state
        contact_user = user_from_email or user_from_phone
        if contact_user:
            self.contact = contact_user
            self.state = constants.user_contact_states['Already Member']
            self.save()

    def get_phone(self):
        phone = ''
        if self.phone_code and self.phone_number:
            phone = '+' + self.phone_code + self.phone_number

        return phone

    @staticmethod
    def create(user, source, first_name=None, last_name='', phone=None, email=None):
        """
        Creates or Updates the contact and associated details like email, phone & name
        :param user:
        :param source:
        :param first_name:
        :param last_name:
        :param phone:
        :param email:
        :return:
        """
        if not validate_email(email) and not validate_phone(phone):
            return None
        contact_from_email = UserContact.get_from_email(user, email)
        contact_from_phone = UserContact.get_from_phone(user, phone)

        if not contact_from_email and not contact_from_phone:
            phone_data = get_phone_or_null(phone)
            contact = UserContact.objects.create(
                source=constants.imported_contact_sources[source],
                first_name=first_name, user=user,
                last_name=last_name)
            if email:
                contact = email.lower()
                contact.save()
            if phone_data:
                contact.phone_number = phone_data['phone_number']
                contact.phone_code = phone_data['phone_code']
                contact.save()

        else:
            contact = contact_from_phone or contact_from_email
            contact.first_name = first_name
            contact.last_name = last_name
            contact.source = source

            if not contact.email and email:
                contact.email = email

            if not contact.phone_number and phone:
                phone_data = get_phone_or_null(phone)
                if phone_data:
                    contact.phone_number = phone_data['phone_number']
                    contact.phone_code = phone_data['phone_code']
                    contact.save()

            contact.save()

        # contact.action_if_contact_on_tc(email=email, phone=phone)
        return contact

    @staticmethod
    def state_transition(invitor, invitee):
        """
        :param user_username: A invitee's username inviting contact
        :param contact: A auth.User for contact that got invited
        :return:
        """
        email = invitee.email
        phone = invitee.userprofile.get_raw_full_primary_phone_number()

        query = UserContact.objects.filter(Q(email=email) | Q(phone=phone))

        if invitee:
            query.update(contact=invitee)
            query.update(state=constants.user_contact_states['Already Member'])

        if invitor and invitee:
            try:
                successful_contact = UserContact.objects.filter(user=invitor, contact=invitee).first()
                if successful_contact:
                    successful_contact.state = constants.user_contact_states['Contact Joined']
                    successful_contact.save()
                    # email to invitor
                    # notifications.notify_invitor_of_successfull_invite(successful_contact)
            except Exception as e:
                logger.error(e)
                pass

    @staticmethod
    def get_contacts(user, state=None, offset=None):
        """
        Function to get contacts for a user
        :param user:
        :param state:
        :param offset:
        :return:
        """
        if state is not None and offset is not None:
            contacts = UserContact.objects.filter(user=user, state=state).order_by("first_name")[offset: offset + 20]
        elif state is not None and offset == 0:
            contacts = UserContact.objects.filter(user=user, state=state).order_by("first_name")
        elif state is None and offset is not None:
            contacts = UserContact.objects.filter(user=user).order_by("first_name")[offset: offset + 20]
        elif state is None and offset is None:
            contacts = UserContact.objects.filter(user=user).order_by("first_name")
        return contacts

    @staticmethod
    def get_contacts_not_on_tc(user, offset=0):
        """
        Function to get contacts, that are not TapChief users.
        So allowed states are ['Invite Pending', 'Invite Sent', 'Invite Reminder Sent']
        :param user:
        :param offset:
        :return:
        """
        allowed_states = [constants.user_contact_states[x] for x in
                          ['Invite Pending', 'Invite Sent', 'Invite Reminder Sent']]
        contacts = UserContact.objects.filter(user=user, state__in=allowed_states).order_by("first_name").exclude(
            email__isnull=True).exclude(email__exact='')[offset: offset + 12]
        return contacts

    @staticmethod
    def get_contacts_on_tc(user, offset=0):
        """
        Function to get contacts, that are TapChief users.
        So allowed states are ['Already Member', 'Contact Joined']
        :param user:
        :param offset:
        :return:
        """
        limit = 10
        allowed_states = [constants.user_contact_states[x] for x in ['Already Member', 'Invite Success', 'Invite Failure']]
        contacts = UserContact.objects.filter(user=user, state__in=allowed_states).order_by("first_name")[
                   offset: offset + limit]
        contact_pks = contacts.values_list('contact', flat=True)
        data = {'contacts': contacts, 'contact_pks': contact_pks}
        return data

    @staticmethod
    def get_count_of_contacts(user, state=None):
        """
        Function to count number of contacts imported by user
        :param user:
        :param state:
        :return:
        """
        if state is not None:
            return UserContact.objects.filter(user=user, state=state).count()
        else:
            return UserContact.objects.filter(user=user).count()

    @staticmethod
    def invite_contacts(user, invite_all=False, deselectd_ids=[], selected_ids=[]):
        """
        Function to send invitation to contacts in state ['Invite Pendint', 'Invite Sent']
        :param user:
        :param invite_all:
        :param deselectd_ids:
        :param selected_ids:
        :return:
        """
        if invite_all:
            query_ = UserContact.objects.filter(~Q(id__in=deselectd_ids), user=user)
        elif not invite_all and len(selected_ids):
            query_ = UserContact.objects.filter(id__in=selected_ids, user=user)

        pending_contacts = query_.filter(state=constants.user_contact_states['Invite Pending'])
        invited_contacts = query_.filter(state=constants.user_contact_states['Invite Sent'],
                                         invited_at__gt=timezone.now() - timedelta(days=7))

        # send invite sms
        # notifications.send_invite_sms_to_contacts(user=user, contacts=pending_contacts)
        # notifications.send_invite_sms_to_contacts(user=user, contacts=invited_contacts)
        # send invite email
        # notifications.send_invite_email_to_contacts(user=user, contacts=pending_contacts)
        # notifications.send_invite_email_to_contacts(user=user, contacts=invited_contacts)

        logger.info('Sending invite to %s pending contacts and %s invited contacts' % (
            pending_contacts.count(), invited_contacts.count(),))

        pending_contacts.update(state=constants.user_contact_states['Invite Sent'])
        invited_contacts.update(state=constants.user_contact_states['Invite Reminder Sent'])

        pending_contacts.update(invited_at=timezone.now())
        invited_contacts.update(invited_at=timezone.now())
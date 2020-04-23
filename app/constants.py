days_of_the_week = {
    'Monday': 'Monday',
    'Tuesday': 'Tuesday',
    'Wednesday': 'Wednesday',
    'Thursday': 'Thursday',
    'Friday': 'Friday',
    'Saturday': 'Saturday',
    'Sunday': 'Sunday',
}
days_of_the_week_choices = [tuple([v, k]) for k, v in days_of_the_week.items()]

language = {
    'hi': 'Hindi',
    'en-uk': 'English UK',
    'en-usa': 'English USA'
}
language_choices = [tuple([v, k]) for k, v in language.items()]

level = {
    'high': 'high',
    'medium': 'medium',
    'low': 'low'

}
level_choices = [tuple([v, k]) for k, v in level.items()]

user_type = {
    'USER': 'USER',
    'BRAND': 'BRAND',
    'COMMUNITY': 'COMMUNITY'
}
user_type_choices = [tuple([v, k]) for k, v in user_type.items()]

user_tag_type = {
    'SOCIAL': 'SOCIAL',
    'PROFESSIONAL': 'PROFESSIONAL',
}
user_tag_type_choices = [tuple([v, k]) for k, v in user_tag_type.items()]

sex = {
    'FEMALE': 'Female',
    'MALE': 'Male',
    'TRANSGENDER': 'Transgender',
    'NOT SPECIFIED': 'Not Specified'
}
sex_choices = [tuple([v, k]) for k, v in sex.items()]

blood_group = {

}

occupation = {
    'STUDENT': 'Student',
    'UNEMPLOYED': 'Unemployed',
    'SELF EMPLOYED': 'Self Employed',
    'PUBLIC EMPLOYEE': 'Public Employee',
    'PRIVATE EMPLOYEE': 'Private Employee',
}
occupation_choices = [tuple([v, k]) for k, v in occupation.items()]

category = {
    'GN': 'General',
    'SC': 'Scheduled categorys',
    'ST': 'Scheduled Tribes',
    'OBC': 'Other Backward Classes',
    'SBC': 'Special Backwar Classes',
    'MN': 'Minority',
}
category_choices = [tuple([v, k]) for k, v in category.items()]

maritial_status = {

}
maritial_status_choices = [tuple([v, k]) for k, v in maritial_status.items()]

education_status = {
    'MATRICULATE': '10th Pass',
    'INTERMEDIATE': '12th Pass',
    'GRADUATE': 'Bachelors(1st) Degree',
    'POST GRADUATE': 'Masters(2nd) Degree',
}
education_status_choices = [tuple([v, k]) for k, v in education_status.items()]

income_status = {
    'POOR': 'Earning less than 100K per annum',
    'LOW MIDDLE': 'Earning 100K - 400k per annum',
    'HIGH MIDDLE': 'Earning 400K - 1000K per annum',
    'LOW UPPER': 'Earning 1000K - 1500K per annum',
    'HIGH UPPER': 'Earning more than 1500K per annum',
}
income_status_choices = [tuple([v, k]) for k, v in income_status.items()]

linkedin_access_url = "https://api.linkedin.com/v1/people/~:(id,num-connections,picture-url,specialties,positions,public-profile-url,location,headline,first_name,last_name,industry,email-address,summary)?format=json"

ERROR_CONFIG = {
    'ERR-DJNG-001': ("No CODE Passed", "Error Message"),
    'ERR-DJNG-002': ("No Object found", "Error Message"),
    'ERR-DJNG-003': ("Multiple Objects Returned", "Error Message"),
    'ERR-GNRL-001': ("Invalid Phone Number", "Error Message"),
    'ERR-GNRL-002': ("Invalid Email Address", "Error Message"),
    'ERR-AUTH-001': ("Invalid Credentials", "Error Message"),
    'ERR-AUTH-002': ("Unsuccessful exchange of Authorization Code for an Access Token", "Error Message"),
    'ERR-AUTH-003': ("Incorrect password", "Error Message"),
    'ERR-AUTH-004': ("Passwords do not match", "Error Message"),
    'ERR-AUTH-005': ("Invalid Phone OTP", "Error Message"),
    'ERR-USER-001': ("No User found", "Error Message"),
    'ERR-USER-002': ("User Already Exists", "Error Message"),
    'ERR-USER-003': ("User Blocked", "Error Message"),
    'ERR-USER-004': ("User Already Exists with Phone Number", "Error Message"),
    'ERR-USER-005': ("User Already Exists with Email ID", "Error Message"),
    'ERR-USER-006': ("User missing OTP details", "Error Message"),
    'ERR-USER-007': ("User permission denied", "Error Message"),
    'ERR-USER-008': ("User Already Exists with username", "Error Message"),
    'ERR-USER-009': ("User does not exists for given token", "Error Message"),
    'ERR-CONT-001': ("No such contact founder with email", "Error Message"),
    'ERR-CONT-002': ("No such contact founder with phone", "Error Message"),
    'ERR-COMM-001': ("No Community found", "Error Message"),
    'ERR-COMM-002': ("User already registered with community", "Error Message"),
    'ERR-CHAT-001': ("Chat not active", "Error Message"),
    'ERR-CHAT-002': ("Chat with yourself not allowed", "Error Message"),
    'ERR-CHAT-003': ("Details missing to create chat", "Error Message"),
    'ERR-BDCT-001': ("No broadcast feed found", "Error Message"),
    'ERR000D': ("Details Missing", "Error Message"),
    'ERR0001': ("Unsuccessful exchange of Authorization Code for an Access Token", "Error Message"),
    'ERR0002': ("Linkedin Access Token not present in LinkedIn response", "Error Message"),
    'ERR0003': ("Unmatching User from UserLinkedInData Object and Function Parameter", "Error Message"),
    'ERR0006': ("User Blocked", "Error Message"),
}

imported_contact_sources = {
    "LINKEDIN": "0",
    "GOOGLE": "1",
    "LINK": "2",
    "PHONE": "3",
}
imported_contact_sources_choices = [tuple([v, k]) for k, v in imported_contact_sources.items()]

user_contact_states = {
    "Invite Pending": "0",
    "Invite Sent": "1",
    "Invite Reminder Sent": "2",
    "Already Member": "3",
    "Invite Success": "4",
    "Invite Failure": "5",
}
user_contact_states_choices = [tuple([v, k]) for k, v in user_contact_states.items()]

story_types = {
    'POST': 'POST',
    'AMA': 'AMA',
    'IMAGE': 'IMAGE',
    'GALLERY': 'GALLERY',
    'VIDEO': 'VIDEO',
    'AUDIO': 'AUDIO'
}
story_types_choices = [tuple([v, k]) for k, v in story_types.items()]

content_types = {
    'NEWS': 'NEWS',
    'ARTICLE': 'ARTICLE',
    'VIDEO': 'VIDEO',
    'AUDIO': 'AUDIO',
    'STORY': 'STORY'
}
content_types_choices = [tuple([v, k]) for k, v in content_types.items()]
content_types_list = [k[0] for k in content_types.items()]


story_feed_types = {
    'WORK_OPPORTUNITY': 'WORK_OPPORTUNITY',
    'CONNECTION_REQUEST': 'CONNECTION_REQUEST',
    'SELF_INTRODUCTION': 'SELF_INTRODUCTION'
}
story_feed_types_choices = [tuple([v, k]) for k, v in story_feed_types.items()]

broadcast_feed_types = {
    'CITY': 'CITY',
    'INTEREST': 'INTEREST',
    'CONNECTION': 'CONNECTION'
}
broadcast_feed_types_choices = [tuple([v, k]) for k, v in broadcast_feed_types.items()]

user_community_assoc = {
    'EVENT': 'EVENT',
    'SIGNUP': 'SIGNUP'
}
user_community_assoc_choices = [tuple([v, k]) for k, v in user_community_assoc.items()]

chat_type_states = {
    'TEXT': 'TEXT',
    'FILE': 'FILE',
    'ACTIONABLE': 'ACTIONABLE',
}
chat_type_states_choices = [tuple([v, k]) for k, v in chat_type_states.items()]

reference_type_states = {
    'STORY': 'STORY',
    'BROADCAST': 'BROADCAST',
    'CONNECTION': 'CONNECTION'
}
reference_type_states_choices = [tuple([v, k]) for k, v in reference_type_states.items()]

notification_type_states = {
    'NEW_COMMENT_ON_BROADCAST': 'NEW_COMMENT_ON_BROADCAST',
    'NEW_FOLLOWER': 'NEW_FOLLOWER',
    'NEW_MESSAGE': 'NEW_MESSAGE'
}
notification_type_states_choices = [tuple([v, k]) for k, v in notification_type_states.items()]

reference_type_states_choices = [tuple([v, k]) for k, v in reference_type_states.items()]

internal_poc = {
    'HARSH GUPTA': 'HARSH GUPTA',
    'SAKSHAM JAIN': 'SAKSHAM JAIN',
}
internal_poc_choices = [tuple([v, k]) for k, v in internal_poc.items()]
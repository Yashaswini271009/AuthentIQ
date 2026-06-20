

# Create your views here.
from django.shortcuts import render
import tweepy
from django.conf import settings
from datetime import datetime, timezone  # <<< UPDATED: imported timezone

# Authenticate using Bearer Token
client = tweepy.Client(bearer_token=settings.FAKEPROFILE_BEARER_TOKEN)

def calculate_fakeness(user):
    score = 0

    # Profile picture default check
    if "default_profile" in user.profile_image_url:
        score += 20

    # Bio check
    if not user.description or len(user.description.strip()) < 5:
        score += 20

    # Followers vs Following check
    followers = user.public_metrics.get('followers_count', 0)
    following = user.public_metrics.get('following_count', 0)
    if followers < 10 and following > 300:
        score += 20

    # Tweets count check
    tweets = user.public_metrics.get('tweet_count', 0)
    if tweets < 10:
        score += 20

    # Account age check
    created_at = user.created_at
    if created_at:
        if created_at.tzinfo is None:  # <<< UPDATED: Ensure created_at is timezone-aware
            created_at = created_at.replace(tzinfo=timezone.utc)

        account_age_days = (datetime.now(timezone.utc) - created_at).days  # <<< UPDATED: changed utcnow() to now(timezone.utc)

        if account_age_days < 90:
            score += 20

    return score

def detect(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').lstrip('@')

        if not username:
            return render(request, 'x/detect.html', {'error': 'Username not provided.'})

        try:
            user_response = client.get_user(
                username=username,
                user_fields=["profile_image_url", "description", "created_at", "public_metrics"]
            )

            user = user_response.data

            if user:
                user_data = {
                    'name': user.name,
                    'followers_count': user.public_metrics.get('followers_count', 0),
                    'following_count': user.public_metrics.get('following_count', 0),
                    'tweet_count': user.public_metrics.get('tweet_count', 0),
                    'profile_image_url': user.profile_image_url,
                    'description': user.description,
                    'created_at': user.created_at.strftime('%Y-%m-%d') if user.created_at else 'Unknown'
                }

                fakeness_score = calculate_fakeness(user)
                classification = 'Fake Profile' if fakeness_score > 50 else 'Real Profile'

                result = {
                    'username': username,
                    'classification': classification,
                    'fakeness_percentage': fakeness_score,
                    'user_data': user_data
                }

                return render(request, 'x/detect.html', {'result': result})

            else:
                return render(request, 'x/detect.html', {'error': 'User data is incomplete or unavailable.'})

        except tweepy.TooManyRequests:
            return render(request, 'x/detect.html', {'error': 'Rate limit exceeded. Please try again later.'})
        except tweepy.NotFound:
            return render(request, 'x/detect.html', {'error': 'Username not found.'})
        except tweepy.TweepyException as e:
            return render(request, 'x/detect.html', {'error': f"Error fetching data: {str(e)}"})

    return render(request, 'x/detect.html')


def x_page(request):
    obj, _ = PlatformVisit.objects.get_or_create(platform='x')
    obj.count += 1
    obj.save()
    return render(request, 'detect.html')   #made a chnge here from x_page to detect.html


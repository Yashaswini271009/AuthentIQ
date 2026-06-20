
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import requests
import instaloader

@csrf_exempt
def detect_profile(request):
    L = instaloader.Instaloader()

    if request.method == "POST":
        username = request.POST.get("username")
        print("Username received:", username)

        try:
            profile = instaloader.Profile.from_username(L.context, username)
        except Exception as e:
            return render(request, "instagram/detect.html", {
                "error": f"Could not retrieve profile data for @{username}: {str(e)}"
            })

        # Extract profile data
        full_name = profile.full_name or ""
        bio = profile.biography or ""
        followers = profile.followers
        following = profile.followees
        posts = profile.mediacount
        profile_pic = bool(profile.profile_pic_url)
        ip_address = request.POST.get("ip_address")  # Optional IP input

        # Detection logic
        reasons_fake = []
        reasons_real = []
        score = 0

        if posts == 0:
            reasons_fake.append("No posts at all — suspicious inactivity.")
        elif posts < 5:
            reasons_fake.append("Very few posts — could be inactive or fake.")
        else:
            reasons_real.append("Active posting — feels real.")
            score += 1

        if followers == 0 or following / (followers + 1) > 2:
            reasons_fake.append("Unusual follower-following ratio.")
        else:
            reasons_real.append("Decent follower count — feels organic.")
            score += 1

        if profile_pic:
            reasons_real.append("Profile picture present — looks personal.")
            score += 1
        else:
            reasons_fake.append("Missing profile picture.")

        if len(bio.strip()) < 10:
            reasons_fake.append("Very short or empty bio.")
        else:
            reasons_real.append("Bio looks real — effort put into the profile.")
            score += 1

        if full_name.strip():
            reasons_real.append("Full name provided — not hiding identity.")
            score += 1
        else:
            reasons_fake.append("No full name — could be suspicious.")

        # Final verdict logic
        profile_type = "Fake"
        if score == 5:
            profile_type = "Genuine"
        elif score >= 3:
            profile_type = "Suspicious but Chill"

        # Optional IP-based location data
        geo_data = None
        if ip_address:
            try:
                response = requests.get(f"https://ipinfo.io/{ip_address}/json")
                if response.status_code == 200:
                    data = response.json()
                    location = f"{data.get('city', '')}, {data.get('region', '')}, {data.get('country', '')}"
                    geo_data = {
                        "ip": ip_address,
                        "location": location
                    }
            except:
                geo_data = None

        # Final context values
        profile_info = {
            "username": username,
            "full_name": full_name,
            "bio": bio,
            "followers": followers,
            "following": following,
            "posts": posts
        }

        vibe_score = {
            "score": score * 20,  # Convert score (0–5) into percentage for visual bar
            "reasons": reasons_real if score >= 3 else reasons_fake
        }

        return render(request, "instagram/detect.html", {
            "profile": profile_info,
            "vibe_score": vibe_score,
            "profile_type": profile_type,
            "geo": geo_data
        })

    return render(request, "instagram/home.html")


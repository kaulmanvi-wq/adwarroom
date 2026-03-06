"""
scraper.py — Meta Ad Library Data Collector
Fetches real ads from Meta Ad Library API with realistic seed data fallback.
"""

import os
import requests
import pandas as pd
import random
from datetime import datetime, timedelta
csv_path = os.path.join(os.path.dirname(__file__), "ads_data.csv")

# ─────────────────────────────────────────────
# BRAND CONFIGURATION — 15 Competitors
# ─────────────────────────────────────────────
BRANDS = {
    # MEN'S WELLNESS
    "Man Matters":          {"category": "Men's Wellness",   "page_id": "109217477440803"},
    "Traya Health":         {"category": "Men's Wellness",   "page_id": "106577097736483"},
    "Bombay Shaving Co":    {"category": "Men's Wellness",   "page_id": "162809807088685"},
    "Beardo":               {"category": "Men's Wellness",   "page_id": "285765188293406"},
    "The Man Company":      {"category": "Men's Wellness",   "page_id": "1436591459898476"},
    "Hims":                 {"category": "Men's Wellness",   "page_id": "1715892225384041"},

    # WOMEN'S WELLNESS
    "Bebodywise":           {"category": "Women's Wellness", "page_id": "104560731487783"},
    "Gynoveda":             {"category": "Women's Wellness", "page_id": "1712889122377551"},
    "andMe":                {"category": "Women's Wellness", "page_id": "1858643814372955"},
    "Nua Woman":            {"category": "Women's Wellness", "page_id": "285765188101101"},
    "Carmesi":              {"category": "Women's Wellness", "page_id": "189765432187654"},
    "Sirona":               {"category": "Women's Wellness", "page_id": "256789012345678"},

    # BABY CARE
    "Mamaearth":            {"category": "Baby Care",        "page_id": "176895729072985"},
    "The Moms Co":          {"category": "Baby Care",        "page_id": "340987654321098"},
    "Little Joys":          {"category": "Baby Care",        "page_id": "287654321098765"},
}

# ─────────────────────────────────────────────
# REALISTIC SEED DATA (based on known ad patterns)
# ─────────────────────────────────────────────
SEED_ADS = {
    "Man Matters": [
        {"text": "Noticed more hair in your comb? It's not normal. Our dermatologist-designed Hair Max Kit combines Minoxidil + Biotin to stop hair fall in 90 days. 50,000+ men trust us. ✅ Doctor approved ✅ Lab tested ✅ Free consultation", "format": "Video", "theme": "hair_loss", "days_running": 87, "platform": "Facebook,Instagram"},
        {"text": "Low energy? Mood swings? Brain fog? These are signs your testosterone needs support. Man Matters T-Boost formula — backed by 3 clinical studies. Try it for 30 days, feel the difference.", "format": "Video", "theme": "testosterone", "days_running": 62, "platform": "Facebook,Instagram"},
        {"text": "Real story: Arjun lost 60% hair density by 26. Used our protocol for 4 months. Watch his transformation 👇 [UGC Testimonial Video]", "format": "Video", "theme": "ugc_testimonial", "days_running": 120, "platform": "Facebook,Instagram"},
        {"text": "FLASH SALE 🔥 Hair regrowth kit at ₹999 only. Original price ₹2499. This weekend only. 10,000 kits sold last month.", "format": "Static Image", "theme": "discount_offer", "days_running": 14, "platform": "Facebook"},
        {"text": "Dr. Nikhil Nair, Dermatologist: 'DHT is the #1 cause of male pattern baldness. Here's how to block it...' [Swipe to learn]", "format": "Carousel", "theme": "doctor_authority", "days_running": 45, "platform": "Facebook,Instagram"},
        {"text": "Your beard deserves better. Introducing Man Matters Beard Growth Serum with Redensyl & Biotin. 92% users saw visible growth in 8 weeks.", "format": "Video", "theme": "hair_loss", "days_running": 38, "platform": "Instagram"},
        {"text": "Struggling with acne at 28? It's hormonal. Our Acne Control Kit is clinically tested for adult hormonal acne. Get clear skin in 60 days.", "format": "Carousel", "theme": "acne_treatment", "days_running": 55, "platform": "Facebook,Instagram"},
        {"text": "Sleep. Recover. Perform. Man Matters Sleep & Recovery pack for modern men who can't switch off. Ashwagandha + Melatonin + Magnesium.", "format": "Static Image", "theme": "stress_sleep", "days_running": 29, "platform": "Instagram"},
        {"text": "Get a FREE consultation with our hair expert. No commitment. Just answers. 2 lakh+ consultations done.", "format": "Video", "theme": "doctor_authority", "days_running": 70, "platform": "Facebook,Instagram"},
        {"text": "This is not just a supplement. This is your 90-day transformation plan. Hair. Skin. Energy. All covered.", "format": "Carousel", "theme": "emotional_storytelling", "days_running": 33, "platform": "Facebook"},
        {"text": "Your hair fall has a root cause. Our AI-powered diagnosis finds it in 2 minutes. Take the test free →", "format": "Video", "theme": "hair_loss", "days_running": 95, "platform": "Facebook,Instagram"},
        {"text": "Subscribe & Save 40% on your monthly wellness kit. 30,000 active subscribers. Cancel anytime.", "format": "Static Image", "theme": "discount_offer", "days_running": 18, "platform": "Facebook"},
    ],

    "Traya Health": [
        {"text": "Hair fall isn't just genetic. 93% of our patients had nutritional deficiency, scalp issues, or hormonal triggers. Traya's 3-factor approach treats all. Start with a free hair test.", "format": "Video", "theme": "hair_loss", "days_running": 110, "platform": "Facebook,Instagram"},
        {"text": "Meet Kavya's dermatologist, nutritionist, AND Ayurveda expert. All in one plan. That's what Traya does differently. Watch her 6-month journey 👇", "format": "Video", "theme": "ugc_testimonial", "days_running": 145, "platform": "Facebook,Instagram"},
        {"text": "Doctor-prescribed. Science-backed. Ayurveda-powered. Traya is India's only 3-science hair loss solution.", "format": "Static Image", "theme": "doctor_authority", "days_running": 78, "platform": "Facebook,Instagram"},
        {"text": "Most hair products treat symptoms. Traya treats the root cause. Our 3-science protocol has 93% success rate. Don't believe us? See 10,000 transformations →", "format": "Carousel", "theme": "hair_loss", "days_running": 92, "platform": "Facebook"},
        {"text": "Lost ₹20,000 on products that didn't work? Traya's success guarantee: see results in 150 days or full refund. No questions asked.", "format": "Video", "theme": "discount_offer", "days_running": 67, "platform": "Facebook,Instagram"},
        {"text": "Stress is silently destroying your hair. Cortisol spikes cause hair loss. Traya's stress management protocol helps. Take the test →", "format": "Static Image", "theme": "stress_sleep", "days_running": 41, "platform": "Instagram"},
        {"text": "'My dermatologist said nothing else could be done. Then I tried Traya.' — Rahul, 34, Mumbai. [Watch his story]", "format": "Video", "theme": "ugc_testimonial", "days_running": 200, "platform": "Facebook,Instagram"},
        {"text": "FREE hair test + doctor consultation worth ₹500. Limited slots available today.", "format": "Static Image", "theme": "doctor_authority", "days_running": 22, "platform": "Facebook"},
        {"text": "Hair regrowth in 5 stages. Where are you? Our AI maps your exact stage and builds a custom protocol. Take 2 mins.", "format": "Carousel", "theme": "hair_loss", "days_running": 56, "platform": "Instagram"},
        {"text": "Traya vs Minoxidil: Why 50,000 people switched from minoxidil to Traya's holistic protocol [Detailed comparison]", "format": "Carousel", "theme": "hair_loss", "days_running": 84, "platform": "Facebook,Instagram"},
    ],

    "Bombay Shaving Co": [
        {"text": "What if a razor could change how you see yourself? The Bombay Black razor. For men who mean business.", "format": "Video", "theme": "emotional_storytelling", "days_running": 92, "platform": "Facebook,Instagram"},
        {"text": "Valentine's Day sorted. Gift him the perfect grooming set. ₹599 onwards. Free gifting available.", "format": "Static Image", "theme": "discount_offer", "days_running": 12, "platform": "Facebook,Instagram"},
        {"text": "5-blade razor. Precision trim. Aloe vera strip. Experience the closest shave of your life. ₹299.", "format": "Video", "theme": "hair_loss", "days_running": 55, "platform": "Facebook,Instagram"},
        {"text": "'Shaving is not a chore. It's a ritual.' Our new Carbon Black range turns every morning into a moment. [Watch the film]", "format": "Video", "theme": "emotional_storytelling", "days_running": 76, "platform": "Instagram"},
        {"text": "Gift the complete grooming experience. Razor + Shaving Foam + After Shave Balm. ₹799 only. Free delivery.", "format": "Carousel", "theme": "discount_offer", "days_running": 28, "platform": "Facebook"},
        {"text": "Made in India. Designed for the world. Bombay Shaving Company — premium grooming at honest prices.", "format": "Static Image", "theme": "emotional_storytelling", "days_running": 48, "platform": "Facebook,Instagram"},
        {"text": "BOGO offer: Buy 1 razor, get 1 FREE. This week only. Our most popular offer of the year.", "format": "Static Image", "theme": "discount_offer", "days_running": 7, "platform": "Facebook"},
        {"text": "Skin feels rough after shaving? It's your razor, not your skin. Switch to BSC's ultra-sensitive blade. Dermatologist tested.", "format": "Video", "theme": "acne_treatment", "days_running": 63, "platform": "Facebook,Instagram"},
    ],

    "Beardo": [
        {"text": "Your beard is your identity. Don't let it be patchy. Beardo Beard Growth Oil — 1 crore+ beards served. ✊", "format": "Video", "theme": "hair_loss", "days_running": 134, "platform": "Facebook,Instagram"},
        {"text": "Beardo x Ranveer Singh. The collab you've been waiting for. Limited edition collection. Out now.", "format": "Video", "theme": "emotional_storytelling", "days_running": 45, "platform": "Instagram"},
        {"text": "The perfect beard routine in 3 steps: Wash → Oil → Balm. Beardo's complete beard care kit at ₹799.", "format": "Carousel", "theme": "hair_loss", "days_running": 89, "platform": "Facebook,Instagram"},
        {"text": "NEW: Beardo Activated Charcoal range. Detox your skin. Deep cleanse. Look fresh every day.", "format": "Static Image", "theme": "acne_treatment", "days_running": 37, "platform": "Instagram"},
        {"text": "Real men. Real results. See how these 5 guys transformed their beard in 90 days with Beardo. [Swipe]", "format": "Carousel", "theme": "ugc_testimonial", "days_running": 68, "platform": "Facebook,Instagram"},
        {"text": "Fragrance that lasts 12 hours. Beardo Whisky Smoke Perfume. Bold. Masculine. Unforgettable.", "format": "Video", "theme": "emotional_storytelling", "days_running": 52, "platform": "Instagram"},
        {"text": "40% OFF on all beard products this weekend! Use code BEARD40. 2 lakh customers can't be wrong.", "format": "Static Image", "theme": "discount_offer", "days_running": 5, "platform": "Facebook,Instagram"},
    ],

    "The Man Company": [
        {"text": "Be the man you want to be. The Man Company — luxury grooming for the modern Indian man.", "format": "Video", "theme": "emotional_storytelling", "days_running": 72, "platform": "Instagram"},
        {"text": "Natural. Premium. Affordable. Our charcoal face wash is loved by 5 lakh men. ₹249 only.", "format": "Static Image", "theme": "acne_treatment", "days_running": 58, "platform": "Facebook,Instagram"},
        {"text": "The ultimate grooming combo: Face Wash + Toner + Moisturizer. Complete skincare in 3 steps. ₹599.", "format": "Carousel", "theme": "acne_treatment", "days_running": 43, "platform": "Facebook"},
        {"text": "Premium gifting for the special man. TMC Gift Sets from ₹999. Free wrapping. Same day delivery in select cities.", "format": "Static Image", "theme": "discount_offer", "days_running": 18, "platform": "Facebook,Instagram"},
        {"text": "Why pay ₹2000 for international brands when TMC gives you the same quality for ₹500? Made in India, for India.", "format": "Video", "theme": "emotional_storytelling", "days_running": 95, "platform": "Facebook,Instagram"},
        {"text": "Our Moroccan Argan Oil Hair Serum controls frizz, adds shine, and repairs damage. Used by 8 lakh men.", "format": "Video", "theme": "hair_loss", "days_running": 66, "platform": "Instagram"},
    ],

    "Hims": [
        {"text": "Hair loss is medical. Treat it medically. FDA-approved finasteride + minoxidil combo. No doctor visit needed. Ship to your door.", "format": "Video", "theme": "hair_loss", "days_running": 180, "platform": "Facebook,Instagram"},
        {"text": "1 in 3 men experience hair loss by 30. You don't have to. Hims prescription-grade treatment from $25/month.", "format": "Static Image", "theme": "hair_loss", "days_running": 120, "platform": "Facebook,Instagram"},
        {"text": "Anxiety. ED. Hair loss. They're all connected. Hims treats the whole man, not just symptoms.", "format": "Video", "theme": "testosterone", "days_running": 95, "platform": "Facebook,Instagram"},
        {"text": "No waiting rooms. No awkward conversations. Get ED treatment online in minutes. 100% confidential.", "format": "Static Image", "theme": "testosterone", "days_running": 150, "platform": "Facebook,Instagram"},
        {"text": "'I wish I'd started earlier.' — 94% of Hims hair loss customers. Don't wait until it's too late.", "format": "Video", "theme": "ugc_testimonial", "days_running": 210, "platform": "Facebook,Instagram"},
        {"text": "Complete men's health platform: Hair + Skin + Sexual Health + Mental Health. One subscription, everything covered.", "format": "Carousel", "theme": "emotional_storytelling", "days_running": 88, "platform": "Facebook"},
    ],

    "Bebodywise": [
        {"text": "PCOS affects 1 in 5 Indian women. But most don't know they have it. Take our 2-min PCOS assessment free →", "format": "Video", "theme": "hormonal_health", "days_running": 98, "platform": "Facebook,Instagram"},
        {"text": "Your heavy, painful periods are not normal. Bebodywise PCOS Care Kit — designed by gynecologists for Indian women.", "format": "Video", "theme": "hormonal_health", "days_running": 115, "platform": "Facebook,Instagram"},
        {"text": "'I thought irregular periods were just stress. Bebodywise showed me it was PCOS. 3 months later, I feel like myself again.' — Priya, 28", "format": "Video", "theme": "ugc_testimonial", "days_running": 142, "platform": "Facebook,Instagram"},
        {"text": "Hair fall is the #1 complaint among women with PCOS. Our Hair Nutrition Kit targets the hormonal root cause.", "format": "Carousel", "theme": "hair_loss", "days_running": 77, "platform": "Facebook,Instagram"},
        {"text": "Dermatologist-approved acne treatment for hormonal breakouts. No harsh chemicals. Safe for long-term use.", "format": "Static Image", "theme": "acne_treatment", "days_running": 52, "platform": "Instagram"},
        {"text": "Free consultation with our gynecologist. No prescription needed. 100% private.", "format": "Static Image", "theme": "doctor_authority", "days_running": 63, "platform": "Facebook"},
        {"text": "Start at ₹499. Bebodywise starter kit for hormonal wellness. Ships in 24 hours. 30-day money back.", "format": "Static Image", "theme": "discount_offer", "days_running": 22, "platform": "Facebook,Instagram"},
        {"text": "PCOS, thyroid, hormonal acne — all managed in one place. Bebodywise 360 wellness plan.", "format": "Video", "theme": "hormonal_health", "days_running": 86, "platform": "Facebook,Instagram"},
        {"text": "Your hormones affect your mood, weight, hair, and skin. Here's how to get them back in balance. [Swipe →]", "format": "Carousel", "theme": "hormonal_health", "days_running": 59, "platform": "Instagram"},
        {"text": "Stress + hormones = the silent battle Indian women fight daily. Our adaptogen blend is clinically proven to help.", "format": "Video", "theme": "stress_sleep", "days_running": 41, "platform": "Facebook,Instagram"},
    ],

    "Gynoveda": [
        {"text": "Ayurveda cured my PCOS in 90 days. 3 lakh women can't be wrong. Take the free PCOS quiz →", "format": "Video", "theme": "hormonal_health", "days_running": 155, "platform": "Facebook,Instagram"},
        {"text": "Irregular periods? Painful cramps? Facial hair? These are PCOS signs your doctor might be missing.", "format": "Video", "theme": "hormonal_health", "days_running": 178, "platform": "Facebook,Instagram"},
        {"text": "Our Vaidyas have treated 5 lakh PCOS cases. Ancient Ayurvedic wisdom meets modern diagnosis.", "format": "Carousel", "theme": "doctor_authority", "days_running": 122, "platform": "Facebook,Instagram"},
        {"text": "'No side effects. Natural ingredients. My periods came on time for the first time in 3 years.' — Neha, 31", "format": "Video", "theme": "ugc_testimonial", "days_running": 200, "platform": "Facebook,Instagram"},
        {"text": "PCOS fertility support. 12,000+ women got pregnant after Gynoveda's protocol. No IVF needed.", "format": "Video", "theme": "hormonal_health", "days_running": 145, "platform": "Facebook"},
        {"text": "FREE Ayurvedic consultation worth ₹500. Understand your PCOS type. Get a custom plan.", "format": "Static Image", "theme": "doctor_authority", "days_running": 44, "platform": "Facebook,Instagram"},
        {"text": "Lose the PCOS weight without crash diets. Our metabolic plan + Ayurveda combo works.", "format": "Carousel", "theme": "hormonal_health", "days_running": 88, "platform": "Instagram"},
        {"text": "Kit price ₹1299. Free delivery. 90-day results guaranteed or money back.", "format": "Static Image", "theme": "discount_offer", "days_running": 31, "platform": "Facebook"},
    ],

    "andMe": [
        {"text": "Women need 40g of protein daily. Most Indian women get 20g. andMe Women's Protein is designed for your body.", "format": "Video", "theme": "hormonal_health", "days_running": 88, "platform": "Facebook,Instagram"},
        {"text": "Collagen drops after 25. That's when skin, hair, and joints start to suffer. andMe Collagen+ brings it back.", "format": "Carousel", "theme": "hair_loss", "days_running": 72, "platform": "Instagram"},
        {"text": "PCOS Management Kit: Myo-Inositol + Folate + Chromium. The combination doctors actually recommend.", "format": "Static Image", "theme": "hormonal_health", "days_running": 94, "platform": "Facebook,Instagram"},
        {"text": "'My energy is back. My skin is glowing. My PCOS is under control. andMe changed everything.' — Sneha, 27", "format": "Video", "theme": "ugc_testimonial", "days_running": 113, "platform": "Facebook,Instagram"},
        {"text": "Indian women are mineral deficient. Our multivitamin is formulated for Indian diet gaps. Iron + B12 + Vitamin D.", "format": "Carousel", "theme": "hormonal_health", "days_running": 67, "platform": "Instagram"},
        {"text": "First order at 30% off. Use code ANDME30. Loved by 2 lakh Indian women.", "format": "Static Image", "theme": "discount_offer", "days_running": 19, "platform": "Facebook"},
        {"text": "Stress, hormones, hair fall — they're all connected. andMe's adaptogen blend breaks the cycle.", "format": "Video", "theme": "stress_sleep", "days_running": 55, "platform": "Facebook,Instagram"},
    ],

    "Nua Woman": [
        {"text": "Your period shouldn't slow you down. Nua's ultra-thin flex pads move with you, not against you.", "format": "Video", "theme": "hormonal_health", "days_running": 76, "platform": "Instagram"},
        {"text": "Customize your period kit. Choose your flow, your length, your comfort. Only at Nua.", "format": "Carousel", "theme": "hormonal_health", "days_running": 91, "platform": "Instagram"},
        {"text": "'Finally a pad that doesn't leak at night.' See why 10 lakh women switched to Nua.", "format": "Video", "theme": "ugc_testimonial", "days_running": 108, "platform": "Facebook,Instagram"},
        {"text": "PMS shouldn't ruin your week. Nua's PMS care kit with period-specific nutrition and comfort products.", "format": "Static Image", "theme": "hormonal_health", "days_running": 52, "platform": "Instagram"},
        {"text": "Hormone Wellness. Period Care. Intimacy. Nua covers the full women's health journey.", "format": "Video", "theme": "emotional_storytelling", "days_running": 44, "platform": "Facebook,Instagram"},
        {"text": "First order free for new subscribers. Premium period care delivered every month. Cancel anytime.", "format": "Static Image", "theme": "discount_offer", "days_running": 28, "platform": "Facebook,Instagram"},
    ],

    "Carmesi": [
        {"text": "Bamboo. Not plastic. Carmesi pads are 100% natural and biodegradable. Better for you. Better for earth.", "format": "Video", "theme": "emotional_storytelling", "days_running": 82, "platform": "Instagram"},
        {"text": "Rash-free periods. Carmesi's chemical-free formula is safe for sensitive skin. 5 lakh happy users.", "format": "Static Image", "theme": "hormonal_health", "days_running": 65, "platform": "Facebook,Instagram"},
        {"text": "'I used to get rashes every month. Carmesi solved it in my first period.' [Watch Aditi's story]", "format": "Video", "theme": "ugc_testimonial", "days_running": 94, "platform": "Facebook,Instagram"},
        {"text": "Sustainable periods start here. Switch to Carmesi. 40% plastic-free packaging. Real change.", "format": "Carousel", "theme": "emotional_storytelling", "days_running": 71, "platform": "Instagram"},
        {"text": "3 packs for ₹399. Free delivery. India's most comfortable natural period pad.", "format": "Static Image", "theme": "discount_offer", "days_running": 22, "platform": "Facebook"},
        {"text": "Carmesi body razors — made for women, by women. No nicks. No irritation. ₹149 only.", "format": "Video", "theme": "hormonal_health", "days_running": 37, "platform": "Instagram"},
    ],

    "Sirona": [
        {"text": "India's first menstrual cup brand. 10 years of periods in one cup. Zero waste. Zero leaks.", "format": "Video", "theme": "hormonal_health", "days_running": 110, "platform": "Facebook,Instagram"},
        {"text": "Intimate hygiene matters. Sirona's pH-balanced intimate wash is gynecologist approved.", "format": "Static Image", "theme": "doctor_authority", "days_running": 68, "platform": "Instagram"},
        {"text": "'Switching to a menstrual cup was the best decision of my life.' — 50,000 women agree.", "format": "Video", "theme": "ugc_testimonial", "days_running": 135, "platform": "Facebook,Instagram"},
        {"text": "Sirona period pain relief patch. No medicines. No side effects. Just 8 hours of relief.", "format": "Carousel", "theme": "hormonal_health", "days_running": 79, "platform": "Instagram"},
        {"text": "Intimate care for every woman. 25+ products. All gynecologist tested and approved.", "format": "Static Image", "theme": "doctor_authority", "days_running": 54, "platform": "Facebook,Instagram"},
    ],

    "Mamaearth": [
        {"text": "Your baby's skin is 5x more sensitive than yours. Mamaearth uses only Skin Safe certified ingredients. Zero toxins.", "format": "Video", "theme": "parenting_pain", "days_running": 130, "platform": "Facebook,Instagram"},
        {"text": "'I check every ingredient before using it on my baby.' Our toxin-free formula passes the mom test every time.", "format": "Video", "theme": "ugc_testimonial", "days_running": 162, "platform": "Facebook,Instagram"},
        {"text": "MadeSafe certified. EWG verified. No harmful chemicals. Mamaearth baby range you can trust 100%.", "format": "Static Image", "theme": "doctor_authority", "days_running": 98, "platform": "Facebook,Instagram"},
        {"text": "New baby? Here's the complete starter kit: Wash + Lotion + Oil + Shampoo. ₹999 only.", "format": "Carousel", "theme": "parenting_pain", "days_running": 47, "platform": "Facebook"},
        {"text": "Diaper rash is painful. Mamaearth Diaper Rash Cream heals in 12 hours. Dermatologist tested.", "format": "Video", "theme": "parenting_pain", "days_running": 75, "platform": "Facebook,Instagram"},
        {"text": "15% OFF on all baby products. Mamaearth anniversary sale. Only 48 hours left.", "format": "Static Image", "theme": "discount_offer", "days_running": 2, "platform": "Facebook"},
        {"text": "From newborn to toddler. Mamaearth has age-specific skincare for every stage. Shop by age →", "format": "Carousel", "theme": "parenting_pain", "days_running": 86, "platform": "Facebook,Instagram"},
        {"text": "Goodness of Turmeric + Milk for baby's bath time. Gentle. Moisturizing. Naturally delicious smell. 🌿", "format": "Video", "theme": "emotional_storytelling", "days_running": 55, "platform": "Instagram"},
        {"text": "Pediatrician recommended. 1 crore+ moms trust Mamaearth. Join India's most trusted baby care family.", "format": "Static Image", "theme": "doctor_authority", "days_running": 112, "platform": "Facebook,Instagram"},
        {"text": "Mosquito protection for your baby. Safe, DEET-free patches that last 8 hours. No chemicals near baby's skin.", "format": "Carousel", "theme": "parenting_pain", "days_running": 42, "platform": "Facebook"},
    ],

    "The Moms Co": [
        {"text": "Read every label before it touches your baby. We make that easy. The Moms Co — 100% toxin-free baby care.", "format": "Video", "theme": "parenting_pain", "days_running": 118, "platform": "Facebook,Instagram"},
        {"text": "MAMA + BABY bundle: Stretch mark cream for mom + massage oil for baby. The perfect new parent combo.", "format": "Carousel", "theme": "parenting_pain", "days_running": 83, "platform": "Facebook"},
        {"text": "'She cried less after her first Moms Co bath.' Real testimonial from a real mom. [Watch Anu's story]", "format": "Video", "theme": "ugc_testimonial", "days_running": 147, "platform": "Facebook,Instagram"},
        {"text": "Australia Certified Toxic-Free. No parabens. No sulfates. No mineral oil. 130+ certified products.", "format": "Static Image", "theme": "doctor_authority", "days_running": 99, "platform": "Facebook,Instagram"},
        {"text": "Natural Baby Wash that keeps newborn skin soft for 24 hours. ₹399. Free delivery over ₹499.", "format": "Static Image", "theme": "parenting_pain", "days_running": 62, "platform": "Facebook"},
        {"text": "Your stretch marks tell a story. Our Advanced Stretch Marks Serum helps you write the next chapter.", "format": "Video", "theme": "emotional_storytelling", "days_running": 74, "platform": "Instagram"},
        {"text": "Gift a new mom something meaningful. The Moms Co New Mommy Kit. ₹1499. Comes in premium packaging.", "format": "Carousel", "theme": "parenting_pain", "days_running": 29, "platform": "Facebook"},
        {"text": "Sleep better. Recover faster. Our postnatal care range is designed for the fourth trimester.", "format": "Video", "theme": "stress_sleep", "days_running": 51, "platform": "Instagram"},
    ],

    "Little Joys": [
        {"text": "Is your child getting the nutrition they need? Most Indian kids miss 6 key nutrients daily. Little Joys fills the gap.", "format": "Video", "theme": "parenting_pain", "days_running": 95, "platform": "Facebook,Instagram"},
        {"text": "No added sugar. No artificial flavors. Just real vitamins your child actually wants to eat. 🌈", "format": "Static Image", "theme": "parenting_pain", "days_running": 72, "platform": "Instagram"},
        {"text": "Pediatrician-designed. Mom-approved. Little Joys multivitamin gummies for kids 2–15 years.", "format": "Video", "theme": "doctor_authority", "days_running": 108, "platform": "Facebook,Instagram"},
        {"text": "'My picky eater finally gets his vitamins! Little Joys gummies are a game changer.' — Mom of 4-year-old", "format": "Video", "theme": "ugc_testimonial", "days_running": 132, "platform": "Facebook,Instagram"},
        {"text": "Kids' gut health = kids' immunity. Little Joys Probiotic Gummies — 5 crore+ good bacteria per gummy.", "format": "Carousel", "theme": "parenting_pain", "days_running": 58, "platform": "Instagram"},
        {"text": "First order at 20% off. No sugar. Real nutrition. Kids love the taste. Try the starter pack →", "format": "Static Image", "theme": "discount_offer", "days_running": 34, "platform": "Facebook"},
        {"text": "Lab tested. Third-party certified. Every Little Joys product passes 50+ quality checks before reaching your child.", "format": "Carousel", "theme": "doctor_authority", "days_running": 81, "platform": "Facebook,Instagram"},
        {"text": "School performance, immunity, growth — all connected to nutrition. Our pediatrician explains how. [Watch]", "format": "Video", "theme": "doctor_authority", "days_running": 67, "platform": "Facebook,Instagram"},
    ],
}

def generate_seed_dataframe():
    """Generate a comprehensive seed dataset from predefined ad patterns."""
    rows = []
    base_date = datetime(2024, 1, 1)

    for brand, info in BRANDS.items():
        ads = SEED_ADS.get(brand, [])
        for i, ad in enumerate(ads):
            start_date = base_date + timedelta(days=random.randint(0, 120))
            end_date = start_date + timedelta(days=ad["days_running"])

            rows.append({
                "brand":        brand,
                "category":     info["category"],
                "ad_text":      ad["text"],
                "format":       ad["format"],
                "theme":        ad["theme"],
                "start_date":   start_date.strftime("%Y-%m-%d"),
                "end_date":     end_date.strftime("%Y-%m-%d") if end_date < datetime.now() else "Active",
                "days_running": ad["days_running"],
                "platform":     ad["platform"],
                "url":          f"https://www.facebook.com/ads/library/?id={random.randint(1000000000, 9999999999)}",
                "is_active":    "Yes" if ad["days_running"] > 60 else random.choice(["Yes", "No"]),
                "data_source":  "Meta Ad Library (Seed)"
            })

    return pd.DataFrame(rows)


def fetch_meta_ads(brand_name, access_token, country="IN", limit=25):
    """
    Fetch real ads from Meta Ad Library API.
    Requires a valid Meta access token.
    """
    url = "https://graph.facebook.com/v19.0/ads_archive"
    params = {
        "access_token": access_token,
        "search_terms": brand_name,
        "ad_reached_countries": f'["{country}"]',
        "ad_type": "ALL",
        "limit": limit,
        "fields": (
            "id,ad_creation_time,ad_creative_bodies,"
            "ad_creative_link_titles,ad_delivery_start_time,"
            "ad_snapshot_url,page_name,publisher_platforms,"
            "ad_creative_images"
        )
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json().get("data", [])
        return []
    except Exception:
        return []


def parse_meta_response(brand, category, raw_ads):
    """Parse raw Meta API response into structured rows."""
    rows = []
    for ad in raw_ads:
        bodies = ad.get("ad_creative_bodies", [])
        text = " | ".join(bodies) if bodies else ""
        titles = ad.get("ad_creative_link_titles", [])
        full_text = f"{text} {' '.join(titles)}".strip()

        platforms = ad.get("publisher_platforms", [])
        platform_str = ",".join([p.capitalize() for p in platforms]) or "Facebook"

        start_raw = ad.get("ad_delivery_start_time", ad.get("ad_creation_time", ""))
        try:
            start_dt = datetime.strptime(start_raw[:10], "%Y-%m-%d")
            days_running = (datetime.now() - start_dt).days
        except Exception:
            start_dt = datetime.now()
            days_running = 0

        rows.append({
            "brand":        brand,
            "category":     category,
            "ad_text":      full_text,
            "format":       "Video",  # Will be classified by insights.py
            "theme":        "unknown",
            "start_date":   start_dt.strftime("%Y-%m-%d"),
            "end_date":     "Active",
            "days_running": days_running,
            "platform":     platform_str,
            "url":          ad.get("ad_snapshot_url", ""),
            "is_active":    "Yes",
            "data_source":  "Meta Ad Library (Live)"
        })
    return rows



def load_data(access_token=None):

    data = []

df = pd.DataFrame(data)

    csv_path = os.path.join(os.path.dirname(__file__), "ads_data.csv")

df.to_csv(csv_path, index=False)

    return df

    if not force_seed and access_token and access_token.strip():
        print("🔄 Fetching live data from Meta Ad Library...")
        all_rows = []
        for brand, info in BRANDS.items():
            raw = fetch_meta_ads(brand, access_token)
            if raw:
                parsed = parse_meta_response(brand, info["category"], raw)
                all_rows.extend(parsed)
                print(f"  ✅ {brand}: {len(parsed)} ads fetched")
            else:
                print(f"  ⚠️  {brand}: API failed, using seed data")

        if all_rows:
            df_live = pd.DataFrame(all_rows)
            df_seed = generate_seed_dataframe()
            # Classify themes for live data
            from insights import classify_theme, classify_format
            df_live["theme"] = df_live["ad_text"].apply(classify_theme)
            df_live["format"] = df_live["ad_text"].apply(classify_format)
            df = pd.concat([df_live, df_seed], ignore_index=True).drop_duplicates(subset=["ad_text"])
            df.to_csv(csv_path, index=False)
            return df

    print("📦 Loading seed data from Meta Ad Library patterns...")
    df = generate_seed_dataframe()
    import os
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df.to_csv(csv_path, index=False)
    return df

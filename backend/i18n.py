"""
FloodWave - Internationalisation (English / Telugu / Hindi)
=============================================================
Single source of truth for every user-facing string.

    S[key] = (english, telugu, hindi)

Used in three places:
  * Jinja templates      ->  {{ t('key') }}
  * Frontend JavaScript  ->  FW_T('key')   (subset exported by js_strings())
  * Backend responses    ->  flood alerts, recommended actions, error messages

To add a language: add its code to SUPPORTED / LANGS, extend the tuples
in S (and ALERTS / RECOMMENDATIONS below) with one more entry.

NOTE: the flood-alert and recommendation texts are safety-relevant. Have a
native speaker review them before real-world deployment.
"""

from flask import request

SUPPORTED = ("en", "te", "hi")
DEFAULT = "en"
COOKIE_NAME = "fw_lang"
# (code, label shown in the switcher) - labels are in their own script so that
# a Telugu-only reader can always find their language.
LANGS = [("en", "EN"), ("te", "తెలుగు"), ("hi", "हिन्दी")]
_IDX = {code: i for i, code in enumerate(SUPPORTED)}


def get_lang():
    """Cookie -> browser Accept-Language -> English."""
    lang = request.cookies.get(COOKIE_NAME)
    if lang in SUPPORTED:
        return lang
    best = request.accept_languages.best_match(SUPPORTED)
    return best or DEFAULT


# ---------------------------------------------------------------------------
# UI strings
# ---------------------------------------------------------------------------
S = {
    # ---- navigation / layout ------------------------------------------------
    "nav_home": ("Home", "హోమ్", "होम"),
    "nav_prediction": ("Prediction", "అంచనా", "पूर्वानुमान"),
    "nav_dashboard": ("Dashboard", "డాష్‌బోర్డ్", "डैशबोर्ड"),
    "nav_about": ("About", "మా గురించి", "परिचय"),
    "nav_contact": ("Contact", "సంప్రదించండి", "संपर्क"),
    "nav_login": ("Login", "లాగిన్", "लॉगिन"),
    "nav_logout": ("Logout", "లాగ్అవుట్", "लॉगआउट"),
    "nav_signup": ("Sign Up", "సైన్ అప్", "साइन अप"),
    "nav_hi": ("Hi, {name}", "నమస్కారం, {name}", "नमस्ते, {name}"),
    "nav_toggle": ("Toggle menu", "మెనూ తెరవండి", "मेनू खोलें"),
    "lang_label": ("Language", "భాష", "भाषा"),
    "meta_title": ("FloodWave — AI Flood Risk Prediction", "FloodWave — AI వరద ప్రమాద అంచనా", "FloodWave — AI बाढ़ जोखिम पूर्वानुमान"),
    "meta_desc": (
        "FloodWave: AI-powered urban flood risk prediction using machine learning and real-time environmental analytics.",
        "FloodWave: మెషిన్ లెర్నింగ్ మరియు రియల్-టైమ్ పర్యావరణ విశ్లేషణతో AI ఆధారిత వరద ప్రమాద అంచనా.",
        "FloodWave: मशीन लर्निंग और रियल-टाइम पर्यावरणीय विश्लेषण से AI-आधारित बाढ़ जोखिम पूर्वानुमान।"),
    "footer_tagline": (
        "AI-powered urban flood risk prediction, built with machine learning and real-time environmental analytics.",
        "మెషిన్ లెర్నింగ్ మరియు రియల్-టైమ్ పర్యావరణ విశ్లేషణతో రూపొందించిన AI ఆధారిత వరద ప్రమాద అంచనా.",
        "मशीन लर्निंग और रियल-टाइम पर्यावरणीय विश्लेषण पर बना AI-आधारित बाढ़ जोखिम पूर्वानुमान।"),
    "footer_navigate": ("Navigate", "త్వరిత లింకులు", "त्वरित लिंक"),
    "footer_resources": ("Resources", "వనరులు", "संसाधन"),
    "footer_account": ("Account", "ఖాతా", "खाता"),
    "footer_docs": ("Documentation", "డాక్యుమెంటేషన్", "दस्तावेज़"),
    "footer_rights": ("© 2026 FloodWave. All rights reserved.", "© 2026 FloodWave. అన్ని హక్కులు ప్రత్యేకించబడ్డాయి.", "© 2026 FloodWave. सर्वाधिकार सुरक्षित।"),
    "footer_version": ("Version 1.0.0", "వెర్షన్ 1.0.0", "संस्करण 1.0.0"),

    # ---- home ---------------------------------------------------------------
    "title_home": ("FloodWave — Predict Tomorrow's Floods Today", "FloodWave — రేపటి వరదలను ఈరోజే అంచనా వేయండి", "FloodWave — कल की बाढ़ का आज ही पूर्वानुमान"),
    "home_eyebrow": ("AI-Powered Flood Intelligence", "AI ఆధారిత వరద సమాచారం", "AI-संचालित बाढ़ इंटेलिजेंस"),
    "home_h1_pre": ("Predict ", "", ""),
    "home_h1_wave": ("Tomorrow's Floods", "రేపటి వరదలను", "कल की बाढ़ का"),
    "home_h1_post": (" Today", " ఈరోజే అంచనా వేయండి", " आज ही पूर्वानुमान लगाएं"),
    "home_subtitle": (
        "AI-powered flood prediction using machine learning, environmental analytics, and real-time weather intelligence.",
        "మెషిన్ లెర్నింగ్, పర్యావరణ విశ్లేషణ మరియు రియల్-టైమ్ వాతావరణ సమాచారంతో AI ఆధారిత వరద అంచనా.",
        "मशीन लर्निंग, पर्यावरणीय विश्लेषण और रियल-टाइम मौसम जानकारी से AI-आधारित बाढ़ पूर्वानुमान।"),
    "cta_predict": ("Predict Flood Risk", "వరద ప్రమాదాన్ని అంచనా వేయండి", "बाढ़ जोखिम का पूर्वानुमान लगाएं"),
    "cta_learn": ("Learn More", "మరింత తెలుసుకోండి", "और जानें"),
    "stat1": ("ML Models Compared", "పోల్చిన ML మోడళ్లు", "तुलना किए गए ML मॉडल"),
    "stat2": ("Environmental Inputs", "పర్యావరణ ఇన్‌పుట్‌లు", "पर्यावरणीय इनपुट"),
    "stat3": ("Explainable AI", "వివరించగల AI", "व्याख्यात्मक AI"),
    "stat4_v": ("Real-Time", "రియల్-టైమ్", "रियल-टाइम"),
    "stat4": ("Weather Intelligence", "వాతావరణ సమాచారం", "मौसम इंटेलिजेंस"),
    "scroll": ("Scroll", "స్క్రోల్", "स्क्रॉल"),
    "how_eyebrow": ("How It Works", "ఇది ఎలా పనిచేస్తుంది", "यह कैसे काम करता है"),
    "how_h2": (
        "From raw environmental data to actionable flood intelligence",
        "ముడి పర్యావరణ డేటా నుండి ఉపయోగపడే వరద సమాచారం వరకు",
        "कच्चे पर्यावरणीय डेटा से उपयोगी बाढ़ जानकारी तक"),
    "how_p": (
        "FloodWave combines satellite-derived precipitation patterns, terrain data, and urban infrastructure metrics into a single explainable risk score.",
        "FloodWave ఉపగ్రహ ఆధారిత వర్షపాత నమూనాలు, భూభాగ డేటా మరియు పట్టణ మౌలిక సదుపాయాల సూచికలను కలిపి ఒకే వివరించదగిన ప్రమాద స్కోరును ఇస్తుంది.",
        "FloodWave उपग्रह-आधारित वर्षा पैटर्न, भू-भाग डेटा और शहरी बुनियादी ढांचे के मानकों को मिलाकर एक स्पष्ट जोखिम स्कोर देता है।"),
    "f1_t": ("Select a Location", "స్థానాన్ని ఎంచుకోండి", "स्थान चुनें"),
    "f1_p": (
        "Rotate the interactive 3D globe and click anywhere to auto-fill latitude, longitude, country, and city.",
        "ఇంటరాక్టివ్ 3D గ్లోబ్‌ను తిప్పి, ఎక్కడైనా క్లిక్ చేస్తే అక్షాంశం, రేఖాంశం, దేశం, నగరం ఆటోమేటిక్‌గా నిండుతాయి.",
        "इंटरैक्टिव 3D ग्लोब घुमाएं और कहीं भी क्लिक करें; अक्षांश, देशांतर, देश और शहर अपने आप भर जाएंगे।"),
    "f2_t": ("Analyze Environmental Data", "పర్యావరణ డేటాను విశ్లేషించండి", "पर्यावरणीय डेटा का विश्लेषण"),
    "f2_p": (
        "Rainfall, river levels, soil moisture, drainage capacity, and 8 more variables feed a tuned ensemble model.",
        "వర్షపాతం, నదీ నీటి మట్టం, నేల తేమ, డ్రైనేజీ సామర్థ్యం మరియు మరో 8 అంశాలు మెరుగుపరచిన ఎన్సెంబుల్ మోడల్‌కు వెళ్తాయి.",
        "वर्षा, नदी स्तर, मिट्टी की नमी, जल निकासी क्षमता और 8 अन्य कारक एक ट्यून किए गए एन्सेम्बल मॉडल को दिए जाते हैं।"),
    "f3_t": ("Get Explainable Results", "స్పష్టమైన ఫలితాలు పొందండి", "स्पष्ट परिणाम पाएं"),
    "f3_p": (
        "See a color-coded risk verdict, confidence score, SHAP-driven contributing factors, and recommended actions.",
        "రంగులతో ప్రమాద స్థాయి, నమ్మకం స్కోరు, SHAP ఆధారిత కారణాలు మరియు సిఫార్సు చేసిన చర్యలు చూడండి.",
        "रंग-कोडित जोखिम स्तर, विश्वास स्कोर, SHAP-आधारित कारक और सुझाई गई कार्रवाइयाँ देखें।"),
    "rel_eyebrow": ("Built For Reliability", "విశ్వసనీయత కోసం నిర్మించబడింది", "विश्वसनीयता के लिए निर्मित"),
    "rel_h2": ("An enterprise-grade prediction pipeline", "ఎంటర్‌ప్రైజ్ స్థాయి అంచనా వ్యవస్థ", "एंटरप्राइज़-स्तर की पूर्वानुमान प्रणाली"),
    "rel_p": (
        "Multiple gradient-boosting models are trained and benchmarked automatically — the best performer is deployed.",
        "అనేక గ్రేడియంట్-బూస్టింగ్ మోడళ్లు ఆటోమేటిక్‌గా శిక్షణ పొంది పోల్చబడతాయి — ఉత్తమమైనది వినియోగంలోకి వస్తుంది.",
        "कई ग्रेडिएंट-बूस्टिंग मॉडल अपने आप प्रशिक्षित और परखे जाते हैं — सबसे अच्छा मॉडल उपयोग में लाया जाता है।"),
    "r1_t": ("Multi-Source Data", "బహుళ మూలాల డేటా", "बहु-स्रोत डेटा"),
    "r1_p": (
        "Modeled on precipitation, terrain, land-use, and river-discharge characteristics from major public datasets.",
        "ప్రధాన పబ్లిక్ డేటాసెట్ల నుండి వర్షపాతం, భూభాగం, భూ వినియోగం, నదీ ప్రవాహ లక్షణాల ఆధారంగా రూపొందించబడింది.",
        "प्रमुख सार्वजनिक डेटासेट से वर्षा, भू-भाग, भूमि उपयोग और नदी प्रवाह की विशेषताओं पर आधारित।"),
    "r2_t": ("Live Dashboard", "లైవ్ డాష్‌బోర్డ్", "लाइव डैशबोर्ड"),
    "r2_p": (
        "Track prediction history, risk distribution, monthly trends, and model performance in one analytics view.",
        "అంచనాల చరిత్ర, ప్రమాద పంపిణీ, నెలవారీ ధోరణులు, మోడల్ పనితీరును ఒకే విశ్లేషణ వీక్షణలో చూడండి.",
        "पूर्वानुमान इतिहास, जोखिम वितरण, मासिक रुझान और मॉडल प्रदर्शन एक ही विश्लेषण दृश्य में देखें।"),
    "r3_t": ("Actionable Guidance", "ఆచరణాత్మక మార్గదర్శకం", "उपयोगी मार्गदर्शन"),
    "r3_p": (
        "Every prediction pairs a risk tier with clear, tier-specific recommended actions for residents and authorities.",
        "ప్రతి అంచనా ప్రమాద స్థాయితో పాటు నివాసితులు, అధికారులకు స్పష్టమైన సిఫార్సు చర్యలను ఇస్తుంది.",
        "हर पूर्वानुमान के साथ जोखिम स्तर और निवासियों व अधिकारियों के लिए स्पष्ट सुझाई गई कार्रवाइयाँ मिलती हैं।"),
    "cta_h2": ("Ready to see your flood risk?", "మీ వరద ప్రమాదం తెలుసుకోవాలనుకుంటున్నారా?", "अपना बाढ़ जोखिम जानने के लिए तैयार हैं?"),
    "cta_p": (
        "Select any location on the globe and get an AI-driven flood risk assessment in seconds.",
        "గ్లోబ్‌పై ఏదైనా ప్రదేశాన్ని ఎంచుకుని, సెకన్లలో AI ఆధారిత వరద ప్రమాద అంచనా పొందండి.",
        "ग्लोब पर कोई भी स्थान चुनें और कुछ ही सेकंड में AI-आधारित बाढ़ जोखिम आकलन पाएं।"),
    "cta_start": ("Start a Prediction", "అంచనా ప్రారంభించండి", "पूर्वानुमान शुरू करें"),

    # ---- prediction page ----------------------------------------------------
    "title_pred": ("Flood Prediction — FloodWave", "వరద అంచనా — FloodWave", "बाढ़ पूर्वानुमान — FloodWave"),
    "pred_eyebrow": ("Prediction Engine", "అంచనా ఇంజిన్", "पूर्वानुमान इंजन"),
    "pred_h2": (
        "Select a location, review the data, predict the risk",
        "స్థానాన్ని ఎంచుకోండి, డేటాను సమీక్షించండి, ప్రమాదాన్ని అంచనా వేయండి",
        "स्थान चुनें, डेटा देखें, जोखिम का पूर्वानुमान लगाएं"),
    "pred_p": (
        "Rotate the globe or fine-tune the environmental parameters manually before running the model.",
        "మోడల్ నడపడానికి ముందు గ్లోబ్‌ను తిప్పండి లేదా పర్యావరణ విలువలను చేతితో సరిచేయండి.",
        "मॉडल चलाने से पहले ग्लोब घुमाएं या पर्यावरणीय मानों को हाथ से समायोजित करें।"),
    "globe_hint": (
        "Drag to rotate · Scroll to zoom · Click to select a location",
        "తిప్పడానికి డ్రాగ్ చేయండి · జూమ్ కోసం స్క్రోల్ చేయండి · స్థానం ఎంచుకోవడానికి క్లిక్ చేయండి",
        "घुमाने के लिए खींचें · ज़ूम के लिए स्क्रॉल करें · स्थान चुनने के लिए क्लिक करें"),
    "no_location": ("No location selected", "స్థానం ఎంచుకోలేదు", "कोई स्थान नहीं चुना गया"),
    "form_title": ("Environmental Parameters", "పర్యావరణ విలువలు", "पर्यावरणीय मान"),
    "lbl_lat": ("Latitude", "అక్షాంశం", "अक्षांश"),
    "lbl_lon": ("Longitude", "రేఖాంశం", "देशांतर"),
    "ph_globe": ("Select on globe", "గ్లోబ్‌పై ఎంచుకోండి", "ग्लोब पर चुनें"),
    "lbl_country": ("Country", "దేశం", "देश"),
    "ph_country": ("e.g. Japan", "ఉదా. భారతదేశం", "जैसे: भारत"),
    "lbl_state": ("State / Province", "రాష్ట్రం / ప్రావిన్స్", "राज्य / प्रांत"),
    "ph_state": ("e.g. Tokyo", "ఉదా. ఆంధ్రప్రదేశ్", "जैसे: आंध्र प्रदेश"),
    "lbl_city": ("City", "నగరం / ఊరు", "शहर / गाँव"),
    "ph_city": ("e.g. Shibuya", "ఉదా. విజయవాడ", "जैसे: विजयवाड़ा"),
    "lbl_rainfall": ("Rainfall (mm/24h)", "వర్షపాతం (మి.మీ/24 గం)", "वर्षा (मिमी/24 घंटे)"),
    "lbl_temp": ("Temperature (°C)", "ఉష్ణోగ్రత (°C)", "तापमान (°C)"),
    "lbl_humidity": ("Humidity (%)", "తేమ (%)", "आर्द्रता (%)"),
    "lbl_river": ("River Water Level (m)", "నదీ నీటి మట్టం (మీ)", "नदी जल स्तर (मी)"),
    "lbl_elev": ("Elevation (m)", "ఎత్తు (మీ)", "ऊँचाई (मी)"),
    "lbl_soil": ("Soil Moisture (0-1)", "నేల తేమ (0-1)", "मिट्टी की नमी (0-1)"),
    "lbl_drain": ("Drainage Capacity (%)", "డ్రైనేజీ సామర్థ్యం (%)", "जल निकासी क्षमता (%)"),
    "lbl_pop": ("Population Density (per km²)", "జనసాంద్రత (చ.కి.మీ.కు)", "जनसंख्या घनत्व (प्रति किमी²)"),
    "lbl_imperv": ("Impervious Surface (%)", "నీరు ఇంకని ఉపరితలం (%)", "जल-अभेद्य सतह (%)"),
    "lbl_wind": ("Wind Speed (km/h)", "గాలి వేగం (కి.మీ/గం)", "हवा की गति (किमी/घंटा)"),
    "lbl_landuse": ("Land Use Type", "భూ వినియోగ రకం", "भूमि उपयोग प्रकार"),
    "lbl_history": ("Previous Flood History", "గతంలో వరదలు వచ్చాయా", "पहले बाढ़ आई है?"),
    "opt_no": ("No", "లేదు", "नहीं"),
    "opt_yes": ("Yes", "అవును", "हाँ"),
    "landuse_Urban": ("Urban", "పట్టణం", "शहरी"),
    "landuse_Suburban": ("Suburban", "శివారు ప్రాంతం", "उपनगरीय"),
    "landuse_Agricultural": ("Agricultural", "వ్యవసాయ భూమి", "कृषि"),
    "landuse_Forest": ("Forest", "అడవి", "वन"),
    "landuse_Wetland": ("Wetland", "చిత్తడి నేల", "आर्द्रभूमि"),
    "landuse_Coastal": ("Coastal", "తీర ప్రాంతం", "तटीय"),
    "landuse_Barren": ("Barren", "బంజరు భూమి", "बंजर"),

    # ---- prediction JS strings ---------------------------------------------
    "js_resolving": ("Resolving location…", "స్థానాన్ని గుర్తిస్తున్నాం…", "स्थान की पहचान हो रही है…"),
    "js_ocean": ("Ocean / unresolved — enter manually", "సముద్రం / గుర్తించలేదు — చేతితో నమోదు చేయండి", "महासागर / अज्ञात — हाथ से भरें"),
    "js_no_address": (
        "No address found for this point (likely open ocean) — you can type it in manually.",
        "ఈ ప్రదేశానికి చిరునామా దొరకలేదు (బహుశా సముద్రం) — మీరే టైప్ చేయవచ్చు.",
        "इस बिंदु का पता नहीं मिला (संभवतः समुद्र) — आप स्वयं टाइप कर सकते हैं।"),
    "js_geo_unreach": (
        "Couldn't reach geocoding service — enter manually",
        "జియోకోడింగ్ సేవ అందలేదు — చేతితో నమోదు చేయండి",
        "जियोकोडिंग सेवा उपलब्ध नहीं — हाथ से भरें"),
    "js_geo_fail": (
        "Location lookup failed — check your internet connection, then enter city/country manually.",
        "స్థానం గుర్తించడం విఫలమైంది — ఇంటర్నెట్ కనెక్షన్ చూసి, ఊరు/దేశం చేతితో నమోదు చేయండి.",
        "स्थान खोज विफल — इंटरनेट जांचें, फिर शहर/देश हाथ से भरें।"),
    "js_weather_ok": (
        "Environmental data auto-filled ({source})",
        "పర్యావరణ డేటా ఆటోమేటిక్‌గా నిండింది ({source})",
        "पर्यावरणीय डेटा अपने आप भरा गया ({source})"),
    "js_weather_fail": (
        "Couldn't fetch weather data — you can enter values manually.",
        "వాతావరణ డేటా తీసుకురాలేకపోయాం — విలువలను చేతితో నమోదు చేయవచ్చు.",
        "मौसम डेटा नहीं मिला — आप मान हाथ से भर सकते हैं।"),
    "js_predict_fail": ("Prediction failed", "అంచనా విఫలమైంది", "पूर्वानुमान विफल रहा"),
    "js_network": ("Network error — please try again", "నెట్‌వర్క్ లోపం — మళ్లీ ప్రయత్నించండి", "नेटवर्क त्रुटि — कृपया पुनः प्रयास करें"),
    "res_title": ("Prediction Result", "అంచనా ఫలితం", "पूर्वानुमान परिणाम"),
    "res_model": ("Model", "మోడల్", "मॉडल"),
    "res_explain": ("Explainability", "వివరణ పద్ధతి", "व्याख्या विधि"),
    "res_badge": ("{overall} · {prob} Flood Probability", "{overall} · వరద సంభావ్యత: {prob}", "{overall} · बाढ़ की संभावना: {prob}"),
    "res_confidence": ("Confidence", "నమ్మకం స్థాయి", "विश्वास स्तर"),
    "res_factors": ("Contributing Factors", "కారణ అంశాలు", "योगदान देने वाले कारक"),
    "res_actions": ("Recommended Actions", "సిఫార్సు చేసిన చర్యలు", "सुझाई गई कार्रवाइयाँ"),
    "res_nofactors": ("No factor data available.", "కారణ అంశాల డేటా లేదు.", "कारक डेटा उपलब्ध नहीं।"),
    "feature_importance": ("Feature Importance", "ఫీచర్ ప్రాముఖ్యత", "फ़ीचर महत्व"),
    "risk_Low": ("Low", "తక్కువ", "कम"),
    "risk_Medium": ("Medium", "మధ్యస్థం", "मध्यम"),
    "risk_High": ("High", "అధికం", "उच्च"),
    "overall_Safe": ("Safe", "సురక్షితం", "सुरक्षित"),
    "overall_Moderate": ("Moderate", "మోస్తరు", "मध्यम"),
    "overall_Severe": ("Severe", "తీవ్రం", "गंभीर"),

    # ---- feature names (contributing factors / dashboard chart) -------------
    "feat_rainfall_mm": ("Rainfall", "వర్షపాతం", "वर्षा"),
    "feat_temperature_c": ("Temperature", "ఉష్ణోగ్రత", "तापमान"),
    "feat_humidity_pct": ("Humidity", "తేమ", "आर्द्रता"),
    "feat_river_level_m": ("River Water Level", "నదీ నీటి మట్టం", "नदी जल स्तर"),
    "feat_elevation_m": ("Elevation", "ఎత్తు", "ऊँचाई"),
    "feat_soil_moisture": ("Soil Moisture", "నేల తేమ", "मिट्टी की नमी"),
    "feat_drainage_capacity_pct": ("Drainage Capacity", "డ్రైనేజీ సామర్థ్యం", "जल निकासी क्षमता"),
    "feat_population_density": ("Population Density", "జనసాంద్రత", "जनसंख्या घनत्व"),
    "feat_impervious_pct": ("Impervious Surface %", "నీరు ఇంకని ఉపరితలం %", "जल-अभेद्य सतह %"),
    "feat_wind_speed_kmh": ("Wind Speed", "గాలి వేగం", "हवा की गति"),
    "feat_previous_flood_history": ("Previous Flood History", "గతంలో వరదల చరిత్ర", "पूर्व बाढ़ इतिहास"),
    "feat_land_use": ("Land Use: {value}", "భూ వినియోగం: {value}", "भूमि उपयोग: {value}"),

    # ---- dashboard ----------------------------------------------------------
    "title_dash": ("Dashboard — FloodWave", "డాష్‌బోర్డ్ — FloodWave", "डैशबोर्ड — FloodWave"),
    "dash_eyebrow": ("Analytics", "విశ్లేషణ", "विश्लेषण"),
    "dash_h2": ("Flood Risk Dashboard", "వరద ప్రమాద డాష్‌బోర్డ్", "बाढ़ जोखिम डैशबोर्ड"),
    "dash_p": (
        "Prediction history, trends, and model performance at a glance.",
        "అంచనాల చరిత్ర, ధోరణులు, మోడల్ పనితీరు ఒక్క చూపులో.",
        "पूर्वानुमान इतिहास, रुझान और मॉडल प्रदर्शन एक नज़र में।"),
    "dash_loading": ("Loading…", "లోడ్ అవుతోంది…", "लोड हो रहा है…"),
    "chart_trend": ("Monthly Flood Risk Trend", "నెలవారీ వరద ప్రమాద ధోరణి", "मासिक बाढ़ जोखिम रुझान"),
    "chart_dist": ("Risk Distribution", "ప్రమాద పంపిణీ", "जोखिम वितरण"),
    "chart_perf": ("Model Performance Comparison", "మోడల్ పనితీరు పోలిక", "मॉडल प्रदर्शन तुलना"),
    "chart_shap": ("SHAP Feature Importance", "SHAP ఫీచర్ ప్రాముఖ్యత", "SHAP फ़ीचर महत्व"),
    "chart_recent": ("Recent Predictions", "ఇటీవలి అంచనాలు", "हाल के पूर्वानुमान"),
    "dash_export": ("Export to Excel", "ఎక్సెల్‌కు ఎగుమతి చేయండి", "एक्सेल में एक्सपोर्ट करें"),
    "th_location": ("Location", "ప్రదేశం", "स्थान"),
    "th_rainfall": ("Rainfall", "వర్షపాతం", "वर्षा"),
    "th_risk": ("Risk", "ప్రమాదం", "जोखिम"),
    "th_conf": ("Confidence", "నమ్మకం", "विश्वास"),
    "th_date": ("Date", "తేదీ", "तारीख"),
    "kpi_total": ("Total Predictions", "మొత్తం అంచనాలు", "कुल पूर्वानुमान"),
    "kpi_total_sub": ("All-time recorded", "ఇప్పటివరకు నమోదైనవి", "अब तक दर्ज"),
    "kpi_high": ("High-Risk Alerts", "అధిక ప్రమాద హెచ్చరికలు", "उच्च जोखिम अलर्ट"),
    "kpi_high_sub": ("Requiring urgent action", "తక్షణ చర్య అవసరం", "तत्काल कार्रवाई आवश्यक"),
    "kpi_model": ("Best Model", "ఉత్తమ మోడల్", "सर्वश्रेष्ठ मॉडल"),
    "kpi_model_sub": ("Auto-selected", "ఆటోమేటిక్‌గా ఎంపికైంది", "स्वतः चयनित"),
    "kpi_acc": ("Model Accuracy", "మోడల్ కచ్చితత్వం", "मॉडल सटीकता"),
    "kpi_acc_sub": ("Held-out test set", "పరీక్ష డేటాపై", "परीक्षण डेटा पर"),
    "dash_empty": (
        "No predictions yet — run one from the Prediction page.",
        "ఇంకా అంచనాలు లేవు — అంచనా పేజీ నుండి ఒకటి చేయండి.",
        "अभी कोई पूर्वानुमान नहीं — पूर्वानुमान पेज से चलाएं।"),

    # ---- auth ---------------------------------------------------------------
    "title_login": ("Login — FloodWave", "లాగిన్ — FloodWave", "लॉगिन — FloodWave"),
    "title_signup": ("Sign Up — FloodWave", "సైన్ అప్ — FloodWave", "साइन अप — FloodWave"),
    "login_title": ("Welcome Back", "తిరిగి స్వాగతం", "वापसी पर स्वागत है"),
    "login_sub": (
        "Log in to access your prediction history and dashboard.",
        "మీ అంచనాల చరిత్ర మరియు డాష్‌బోర్డ్ చూడటానికి లాగిన్ అవ్వండి.",
        "अपना पूर्वानुमान इतिहास और डैशबोर्ड देखने के लिए लॉग इन करें।"),
    "lbl_email": ("Email", "ఇమెయిల్", "ईमेल"),
    "lbl_password": ("Password", "పాస్‌వర్డ్", "पासवर्ड"),
    "remember": ("Remember Me", "నన్ను గుర్తుంచుకో", "मुझे याद रखें"),
    "forgot": ("Forgot Password?", "పాస్‌వర్డ్ మర్చిపోయారా?", "पासवर्ड भूल गए?"),
    "btn_login": ("Log In", "లాగిన్ అవ్వండి", "लॉग इन करें"),
    "login_foot": ("Don't have an account?", "ఖాతా లేదా?", "खाता नहीं है?"),
    "link_signup": ("Sign up", "సైన్ అప్ చేయండి", "साइन अप करें"),
    "signup_title": ("Create Your Account", "మీ ఖాతాను సృష్టించండి", "अपना खाता बनाएं"),
    "signup_sub": (
        "Join FloodWave to save predictions and track flood risk over time.",
        "అంచనాలను సేవ్ చేసి, కాలక్రమంలో వరద ప్రమాదాన్ని గమనించడానికి FloodWaveలో చేరండి.",
        "पूर्वानुमान सहेजने और समय के साथ बाढ़ जोखिम ट्रैक करने के लिए FloodWave से जुड़ें।"),
    "lbl_fullname": ("Full Name", "పూర్తి పేరు", "पूरा नाम"),
    "ph_fullname": ("Jane Doe", "మీ పూర్తి పేరు", "आपका पूरा नाम"),
    "ph_pw6": ("6+ characters", "6+ అక్షరాలు", "6+ अक्षर"),
    "signup_foot": ("Already have an account?", "ఇప్పటికే ఖాతా ఉందా?", "पहले से खाता है?"),
    "link_login": ("Log in", "లాగిన్ అవ్వండి", "लॉग इन करें"),
    "err_login": ("Invalid email or password.", "ఇమెయిల్ లేదా పాస్‌వర్డ్ తప్పు.", "ईमेल या पासवर्ड गलत है।"),
    "err_signup_fill": (
        "Please fill all fields; password must be 6+ characters.",
        "అన్ని వివరాలు నింపండి; పాస్‌వర్డ్ కనీసం 6 అక్షరాలు ఉండాలి.",
        "कृपया सभी फ़ील्ड भरें; पासवर्ड कम से कम 6 अक्षरों का होना चाहिए।"),
    "err_email_exists": (
        "An account with that email already exists.",
        "ఈ ఇమెయిల్‌తో ఇప్పటికే ఖాతా ఉంది.",
        "इस ईमेल से खाता पहले से मौजूद है।"),
    "err_contact_fill": (
        "Please fill in all required fields.",
        "అవసరమైన అన్ని వివరాలు నింపండి.",
        "कृपया सभी आवश्यक फ़ील्ड भरें।"),
    "err_predict": ("Prediction failed: {err}", "అంచనా విఫలమైంది: {err}", "पूर्वानुमान विफल: {err}"),

    # ---- contact ------------------------------------------------------------
    "title_contact": ("Contact — FloodWave", "సంప్రదించండి — FloodWave", "संपर्क — FloodWave"),
    "contact_eyebrow": ("Get In Touch", "మమ్మల్ని సంప్రదించండి", "संपर्क करें"),
    "contact_h2": ("Contact the FloodWave Team", "FloodWave బృందాన్ని సంప్రదించండి", "FloodWave टीम से संपर्क करें"),
    "contact_p": (
        "Questions about the platform, the model, or partnering on flood-resilience initiatives? Send us a message.",
        "ప్లాట్‌ఫామ్, మోడల్ లేదా వరద-నిరోధక కార్యక్రమాల్లో భాగస్వామ్యం గురించి ప్రశ్నలు ఉన్నాయా? మాకు సందేశం పంపండి.",
        "प्लेटफ़ॉर्म, मॉडल या बाढ़-सहनशीलता पहलों में साझेदारी के बारे में प्रश्न हैं? हमें संदेश भेजें।"),
    "contact_success": (
        "Thanks — your message has been received.",
        "ధన్యవాదాలు — మీ సందేశం అందింది.",
        "धन्यवाद — आपका संदेश मिल गया है।"),
    "lbl_name": ("Name", "పేరు", "नाम"),
    "ph_yourname": ("Your name", "మీ పేరు", "आपका नाम"),
    "lbl_subject": ("Subject", "విషయం", "विषय"),
    "ph_subject": ("How can we help?", "మేము ఎలా సహాయం చేయగలం?", "हम कैसे मदद कर सकते हैं?"),
    "lbl_message": ("Message", "సందేశం", "संदेश"),
    "ph_message": ("Tell us more...", "మరిన్ని వివరాలు చెప్పండి...", "अधिक बताएं..."),
    "btn_send": ("Send Message", "సందేశం పంపండి", "संदेश भेजें"),
    "ci_focus": ("Focus", "దృష్టి సారించే అంశం", "फोकस"),
    "ci_focus_p": (
        "Urban flood risk research & disaster-preparedness tooling",
        "పట్టణ వరద ప్రమాద పరిశోధన మరియు విపత్తు సన్నద్ధత సాధనాలు",
        "शहरी बाढ़ जोखिम अनुसंधान और आपदा-तैयारी उपकरण"),
    "ci_resp": ("Response Time", "స్పందన సమయం", "प्रतिक्रिया समय"),
    "ci_resp_p": (
        "We reply to most messages within 1–2 business days.",
        "చాలా సందేశాలకు 1–2 పని దినాల్లో సమాధానం ఇస్తాం.",
        "हम अधिकांश संदेशों का उत्तर 1–2 कार्य दिवसों में देते हैं।"),

    # ---- about --------------------------------------------------------------
    "title_about": ("About — FloodWave", "మా గురించి — FloodWave", "परिचय — FloodWave"),
    "about_eyebrow": ("About the Platform", "ప్లాట్‌ఫామ్ గురించి", "प्लेटफ़ॉर्म के बारे में"),
    "about_h2": (
        "Explainable AI for urban flood resilience",
        "పట్టణ వరద నిరోధకత కోసం వివరించదగిన AI",
        "शहरी बाढ़ सहनशीलता के लिए व्याख्यात्मक AI"),
    "about_p": (
        "FloodWave brings together machine learning, predictive analytics, and real-time environmental data to help communities anticipate flood risk before it becomes a crisis.",
        "FloodWave మెషిన్ లెర్నింగ్, అంచనా విశ్లేషణలు మరియు రియల్-టైమ్ పర్యావరణ డేటాను కలిపి, సంక్షోభం కాకముందే వరద ప్రమాదాన్ని ముందే గుర్తించడానికి సమాజాలకు సహాయపడుతుంది.",
        "FloodWave मशीन लर्निंग, पूर्वानुमान विश्लेषण और रियल-टाइम पर्यावरणीय डेटा को जोड़कर समुदायों को संकट बनने से पहले बाढ़ जोखिम भांपने में मदद करता है।"),
    "a1_t": ("What is FloodWave?", "FloodWave అంటే ఏమిటి?", "FloodWave क्या है?"),
    "a1_p": (
        "FloodWave is an AI-powered urban flood risk prediction platform. Given a location and a set of environmental parameters, it returns a color-coded flood probability, an overall risk verdict, and a confidence score, backed by an explainable machine learning model.",
        "FloodWave ఒక AI ఆధారిత పట్టణ వరద ప్రమాద అంచనా ప్లాట్‌ఫామ్. ఒక ప్రదేశం మరియు కొన్ని పర్యావరణ విలువలు ఇస్తే, రంగులతో వరద సంభావ్యత, మొత్తం ప్రమాద స్థాయి మరియు నమ్మకం స్కోరును ఇస్తుంది — దీనికి వివరించదగిన మెషిన్ లెర్నింగ్ మోడల్ ఆధారం.",
        "FloodWave एक AI-आधारित शहरी बाढ़ जोखिम पूर्वानुमान प्लेटफ़ॉर्म है। किसी स्थान और कुछ पर्यावरणीय मानों के आधार पर यह रंग-कोडित बाढ़ संभावना, समग्र जोखिम स्तर और विश्वास स्कोर देता है, जिसके पीछे एक व्याख्यात्मक मशीन लर्निंग मॉडल है।"),
    "a2_t": ("Machine Learning", "మెషిన్ లెర్నింగ్", "मशीन लर्निंग"),
    "a2_p": (
        "Several ensemble models — Random Forest, Gradient Boosting, and (where available) XGBoost, LightGBM, and CatBoost — are trained and benchmarked automatically. The model with the strongest weighted F1 score on held-out data is deployed to production.",
        "రాండమ్ ఫారెస్ట్, గ్రేడియంట్ బూస్టింగ్ మరియు (అందుబాటులో ఉంటే) XGBoost, LightGBM, CatBoost వంటి అనేక ఎన్సెంబుల్ మోడళ్లు ఆటోమేటిక్‌గా శిక్షణ పొంది పోల్చబడతాయి. పరీక్ష డేటాపై అత్యధిక వెయిటెడ్ F1 స్కోరు సాధించిన మోడల్ వినియోగంలోకి వస్తుంది.",
        "रैंडम फ़ॉरेस्ट, ग्रेडिएंट बूस्टिंग और (उपलब्ध होने पर) XGBoost, LightGBM व CatBoost जैसे कई एन्सेम्बल मॉडल अपने आप प्रशिक्षित और परखे जाते हैं। परीक्षण डेटा पर सबसे अधिक वेटेड F1 स्कोर वाला मॉडल उपयोग में लाया जाता है।"),
    "a3_t": ("Predictive Analytics", "అంచనా విశ్లేషణలు", "पूर्वानुमान विश्लेषण"),
    "a3_p": (
        "Twelve environmental and infrastructure variables — from rainfall and river level to drainage capacity and population density — feed a composite risk score, visualized live on the dashboard alongside historical trends.",
        "వర్షపాతం, నదీ మట్టం నుండి డ్రైనేజీ సామర్థ్యం, జనసాంద్రత వరకు పన్నెండు పర్యావరణ, మౌలిక సదుపాయాల అంశాలు కలిసి ఒక మిశ్రమ ప్రమాద స్కోరును ఇస్తాయి; దీన్ని డాష్‌బోర్డ్‌లో గత ధోరణులతో పాటు లైవ్‌గా చూడవచ్చు.",
        "वर्षा और नदी स्तर से लेकर जल निकासी क्षमता और जनसंख्या घनत्व तक बारह पर्यावरणीय और बुनियादी ढांचे के कारक मिलकर एक समग्र जोखिम स्कोर बनाते हैं, जिसे डैशबोर्ड पर पिछले रुझानों के साथ लाइव देखा जा सकता है।"),
    "a4_t": ("Explainable AI", "వివరించదగిన AI", "व्याख्यात्मक AI"),
    "a4_p": (
        "When the optional <code>shap</code> package is installed, each prediction is paired with SHAP values that show exactly which variables pushed the risk score up or down — otherwise the app falls back to native model feature-importance rankings.",
        "ఐచ్ఛిక <code>shap</code> ప్యాకేజీ ఇన్‌స్టాల్ చేసి ఉంటే, ప్రతి అంచనాతో SHAP విలువలు వస్తాయి — ఏ అంశాలు ప్రమాద స్కోరును పెంచాయో/తగ్గించాయో అవి స్పష్టంగా చూపిస్తాయి. లేకపోతే మోడల్ స్వంత ఫీచర్ ప్రాముఖ్యత ర్యాంకింగ్‌లు వాడతాం.",
        "वैकल्पिक <code>shap</code> पैकेज स्थापित होने पर हर पूर्वानुमान के साथ SHAP मान मिलते हैं जो दिखाते हैं कि किन कारकों ने जोखिम स्कोर बढ़ाया या घटाया; अन्यथा ऐप मॉडल की अपनी फ़ीचर महत्व रैंकिंग का उपयोग करता है।"),
    "a5_t": ("Datasets", "డేటాసెట్లు", "डेटासेट"),
    "a5_p": (
        "The training pipeline is built around the schema and statistical ranges of well-known public sources — NASA precipitation records, NOAA weather normals, USGS elevation and river discharge, and Copernicus/OSM land-use categories — combined into a unified, feature-engineered dataset.",
        "శిక్షణ వ్యవస్థ ప్రసిద్ధ పబ్లిక్ వనరుల స్కీమా మరియు గణాంక పరిధుల ఆధారంగా రూపొందించబడింది — NASA వర్షపాత రికార్డులు, NOAA వాతావరణ సగటులు, USGS ఎత్తు మరియు నదీ ప్రవాహం, Copernicus/OSM భూ వినియోగ వర్గాలు — వీటిని కలిపి ఏకీకృత డేటాసెట్‌గా తయారు చేశాం.",
        "प्रशिक्षण पाइपलाइन प्रसिद्ध सार्वजनिक स्रोतों के स्कीमा और सांख्यिकीय दायरों पर आधारित है — NASA वर्षा रिकॉर्ड, NOAA मौसम औसत, USGS ऊँचाई व नदी प्रवाह, और Copernicus/OSM भूमि उपयोग श्रेणियाँ — जिन्हें मिलाकर एक एकीकृत डेटासेट बनाया गया है।"),
    "a6_t": ("Technologies Used", "ఉపయోగించిన సాంకేతికతలు", "उपयोग की गई तकनीकें"),
    "a6_p": (
        "Python, Flask, scikit-learn, pandas, NumPy on the backend; Three.js, Plotly, and vanilla JavaScript with CSS glassmorphism on the frontend; SQLite for persistence.",
        "బ్యాకెండ్‌లో Python, Flask, scikit-learn, pandas, NumPy; ఫ్రంటెండ్‌లో Three.js, Plotly, వెనిలా JavaScript మరియు CSS గ్లాస్‌మార్ఫిజం; డేటా నిల్వకు SQLite.",
        "बैकएंड पर Python, Flask, scikit-learn, pandas, NumPy; फ्रंटएंड पर Three.js, Plotly, वैनिला JavaScript और CSS ग्लासमॉर्फिज़्म; डेटा भंडारण के लिए SQLite।"),
}

# ---------------------------------------------------------------------------
# Flood alerts + recommended actions (shown after each prediction)
# ---------------------------------------------------------------------------
# ALERTS[level] = (title, message) each a (en, te, hi) tuple
ALERTS = {
    "Low": (
        ("✅ Low flood risk", "✅ వరద ప్రమాదం తక్కువ", "✅ बाढ़ का जोखिम कम"),
        ("Conditions look safe right now. Keep watching weather updates.",
         "ప్రస్తుతం పరిస్థితి సురక్షితంగా ఉంది. వాతావరణ సమాచారాన్ని గమనిస్తూ ఉండండి.",
         "अभी स्थिति सुरक्षित है। मौसम की जानकारी पर नज़र रखें।"),
    ),
    "Medium": (
        ("⚠️ Flood watch — stay alert", "⚠️ వరద జాగ్రత్త — అప్రమత్తంగా ఉండండి", "⚠️ बाढ़ की चेतावनी — सतर्क रहें"),
        ("Water levels may rise in the next 24–48 hours. Keep an emergency kit ready and know your evacuation route.",
         "రాబోయే 24–48 గంటల్లో నీటి మట్టం పెరిగే అవకాశం ఉంది. అత్యవసర కిట్ సిద్ధంగా ఉంచుకోండి, ఖాళీ చేయాల్సిన మార్గం తెలుసుకోండి.",
         "अगले 24–48 घंटों में जल स्तर बढ़ सकता है। आपातकालीन किट तैयार रखें और निकासी का रास्ता जान लें।"),
    ),
    "High": (
        ("🚨 SEVERE FLOOD WARNING", "🚨 తీవ్రమైన వరద హెచ్చరిక", "🚨 गंभीर बाढ़ चेतावनी"),
        ("Flooding is very likely. Move to higher ground now. Do not walk or drive through flood water. Follow instructions from local authorities.",
         "వరద వచ్చే అవకాశం చాలా ఎక్కువగా ఉంది. వెంటనే ఎత్తైన ప్రదేశానికి వెళ్లండి. వరద నీటిలో నడవకండి, వాహనం నడపకండి. స్థానిక అధికారుల సూచనలు పాటించండి.",
         "बाढ़ की संभावना बहुत अधिक है। तुरंत ऊँचे स्थान पर जाएं। बाढ़ के पानी में पैदल या वाहन से न जाएं। स्थानीय अधिकारियों के निर्देशों का पालन करें।"),
    ),
}

ALERT_DISCLAIMER = (
    "This is an AI-based estimate, not an official warning. Always follow official alerts from local disaster-management authorities.",
    "ఇది AI ఆధారిత అంచనా మాత్రమే, అధికారిక హెచ్చరిక కాదు. స్థానిక విపత్తు నిర్వహణ అధికారుల అధికారిక హెచ్చరికలను తప్పక పాటించండి.",
    "यह AI-आधारित अनुमान है, आधिकारिक चेतावनी नहीं। हमेशा स्थानीय आपदा प्रबंधन अधिकारियों की आधिकारिक चेतावनियों का पालन करें।",
)

RECOMMENDATIONS = {
    "Low": [
        ("Continue routine monitoring of rainfall and river levels.",
         "వర్షపాతం మరియు నదీ నీటి మట్టాలను క్రమం తప్పకుండా గమనిస్తూ ఉండండి.",
         "वर्षा और नदी स्तर की नियमित निगरानी जारी रखें।"),
        ("No immediate action required; review local drainage upkeep seasonally.",
         "తక్షణ చర్య అవసరం లేదు; ప్రతి సీజన్‌లో స్థానిక డ్రైనేజీ నిర్వహణను సమీక్షించండి.",
         "तत्काल कार्रवाई की आवश्यकता नहीं; हर मौसम में स्थानीय जल निकासी के रखरखाव की समीक्षा करें।"),
        ("Keep emergency contacts and flood-alert subscriptions up to date.",
         "అత్యవసర ఫోన్ నంబర్లు మరియు వరద హెచ్చరిక సబ్‌స్క్రిప్షన్లను తాజాగా ఉంచుకోండి.",
         "आपातकालीन संपर्क और बाढ़ अलर्ट सदस्यता अद्यतन रखें।"),
    ],
    "Medium": [
        ("Monitor weather and river-level updates closely over the next 24-48 hours.",
         "రాబోయే 24–48 గంటల్లో వాతావరణ మరియు నదీ మట్టం సమాచారాన్ని జాగ్రత్తగా గమనించండి.",
         "अगले 24–48 घंटों में मौसम और नदी स्तर की जानकारी पर बारीकी से नज़र रखें।"),
        ("Clear local drains and gutters to maximize drainage capacity.",
         "నీరు బాగా పోవడానికి స్థానిక కాలువలు, డ్రైనేజీలను శుభ్రం చేయండి.",
         "जल निकासी बढ़ाने के लिए स्थानीय नालियां और गटर साफ करें।"),
        ("Prepare an emergency kit and review evacuation routes as a precaution.",
         "ముందు జాగ్రత్తగా అత్యవసర కిట్ సిద్ధం చేసి, ఖాళీ చేసే మార్గాలను చూసుకోండి.",
         "सावधानी के तौर पर आपातकालीन किट तैयार करें और निकासी मार्गों की जांच कर लें।"),
        ("Local authorities should consider issuing a flood watch advisory.",
         "స్థానిక అధికారులు వరద జాగ్రత్త సూచన జారీ చేయడాన్ని పరిశీలించాలి.",
         "स्थानीय अधिकारी बाढ़ निगरानी सलाह जारी करने पर विचार करें।"),
    ],
    "High": [
        ("Issue an immediate flood warning to residents in low-lying areas.",
         "లోతట్టు ప్రాంతాల ప్రజలకు వెంటనే వరద హెచ్చరిక జారీ చేయండి.",
         "निचले इलाकों के निवासियों को तुरंत बाढ़ की चेतावनी जारी करें।"),
        ("Activate emergency response and evacuation plans without delay.",
         "అత్యవసర స్పందన మరియు ఖాళీ చేయించే ప్రణాళికలను ఆలస్యం లేకుండా అమలు చేయండి.",
         "आपातकालीन प्रतिक्रिया और निकासी योजनाओं को बिना देरी सक्रिय करें।"),
        ("Coordinate with drainage and river-management authorities to relieve water levels.",
         "నీటి మట్టం తగ్గించడానికి డ్రైనేజీ మరియు నదీ నిర్వహణ అధికారులతో సమన్వయం చేసుకోండి.",
         "जल स्तर कम करने के लिए जल निकासी और नदी प्रबंधन अधिकारियों के साथ समन्वय करें।"),
        ("Suspend non-essential activity in flood-prone zones and secure critical infrastructure.",
         "వరద ప్రమాద ప్రాంతాల్లో అనవసర కార్యకలాపాలను నిలిపివేసి, కీలక మౌలిక సదుపాయాలను కాపాడండి.",
         "बाढ़-संभावित क्षेत्रों में गैर-जरूरी गतिविधियां रोकें और महत्वपूर्ण बुनियादी ढांचे को सुरक्षित करें।"),
    ],
}


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------
def _pick(tup, lang):
    return tup[_IDX.get(lang, 0)]


def translate(key, lang=None, **kwargs):
    """Look up `key` in `lang` (falls back to English, then the key itself)."""
    lang = lang or get_lang()
    entry = S.get(key)
    if entry is None:
        return key
    text = _pick(entry, lang) or entry[0]
    return text.format(**kwargs) if kwargs else text


def alert_for(level, lang):
    """Return {level, title, message, disclaimer} for a Low/Medium/High tier."""
    title, message = ALERTS.get(level, ALERTS["Medium"])
    return {
        "level": level,
        "title": _pick(title, lang),
        "message": _pick(message, lang),
        "disclaimer": _pick(ALERT_DISCLAIMER, lang),
    }


def recommendations_for(level, lang):
    return [_pick(r, lang) for r in RECOMMENDATIONS.get(level, RECOMMENDATIONS["Medium"])]


def feature_label(name, lang):
    """Friendly, translated name for a raw model feature (e.g. 'rainfall_mm')."""
    if name.startswith("land_use_type_"):
        value = name.replace("land_use_type_", "")
        return translate("feat_land_use", lang, value=translate("landuse_" + value, lang))
    key = "feat_" + name
    if key in S:
        return translate(key, lang)
    return name.replace("_", " ").title()


_JS_PREFIXES = ("js_", "res_", "risk_", "overall_", "feat_", "landuse_", "kpi_", "th_",
                "dash_", "chart_", "feature_importance", "lbl_lat", "lbl_lon", "no_location")


def js_strings(lang):
    """Subset of strings exported to the browser as window.FW_I18N."""
    return {k: _pick(v, lang) for k, v in S.items() if k.startswith(_JS_PREFIXES)}

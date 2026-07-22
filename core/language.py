"""
DIA Multi-Language Responses — Legal Agreement Assistant
System Prompt: Professional banking/legal tone, one question at a time,
confirm before API calls, explain results after each call.
Supports: English, Hindi (हिंदी), Marathi (मराठी), German (Deutsch), Mandarin (普通话)
"""

RESPONSES = {
    "English": {
        # ── Greeting ──────────────────────────────────────────────────────────
        "greeting": (
            "Good day, Sir. I am <b>DIA</b> — your AI Legal Agreement Assistant.<br><br>"
            "I am authorised to assist you with the following services:<br>"
            "⚖️ &nbsp;<b>Generate Legal / Bank Agreements</b><br>"
            "🔍 &nbsp;<b>Verify Generated Documents</b><br>"
            "📋 &nbsp;<b>Fetch Your Agreement History</b><br><br>"
            "How may I be of service to you today?"
        ),
        "greeting_audio": (
            "Good day Sir. I am DIA, your AI Legal Agreement Assistant. "
            "I can help you generate legal or bank agreements, verify documents, "
            "or fetch your agreement history. How may I assist you today?"
        ),
        # ── Main menu options ──────────────────────────────────────────────────
        "main_menu": (
            "Please select one of the following options, Sir:<br>"
            "1️⃣ &nbsp;<b>Generate Agreement</b> — Create new or regenerate from history<br>"
            "2️⃣ &nbsp;<b>Verify Document</b> — Validate an existing agreement<br>"
            "3️⃣ &nbsp;<b>Agreement History</b> — View all past documents<br><br>"
            "You may type your choice or select a button below."
        ),
        "main_menu_audio": (
            "Please choose an option Sir. "
            "Option 1: Generate Agreement. "
            "Option 2: Verify Document. "
            "Option 3: View Agreement History."
        ),
        # ── Identity / Name ────────────────────────────────────────────────────
        "ask_name": (
            "Certainly, Sir. Before I proceed, may I request your <b>full name</b>, "
            "so I can retrieve your records from our system?"
        ),
        "ask_name_audio": (
            "Certainly Sir. Before I proceed, may I request your full name "
            "so I can retrieve your records?"
        ),
        # ── Fetching history ───────────────────────────────────────────────────
        "fetching": (
            "Thank you, Sir. Accessing the secure document repository for <b>{name}</b>. "
            "Please hold on for a moment..."
        ),
        "fetching_audio": (
            "Thank you Sir. Accessing the secure document repository for {name}. "
            "Please hold on."
        ),
        "history_found": (
            "Sir, I have retrieved <b>{count}</b> agreement record(s) on file for <b>{name}</b>. "
            "Please review the documents displayed below."
        ),
        "history_found_audio": (
            "Sir, I found {count} agreement records on file for {name}. "
            "Please review them on screen."
        ),
        "history_empty": (
            "Sir, I could not locate any existing agreement records for <b>{name}</b> "
            "in our system. Would you like to <b>create a new agreement</b> instead?"
        ),
        "history_empty_audio": (
            "Sir, no existing records were found for {name}. "
            "Would you like to create a new agreement instead?"
        ),
        # ── Post-history choice ────────────────────────────────────────────────
        "post_history": (
            "Sir, how would you like to proceed?<br><br>"
            "🔄 &nbsp;<b>Regenerate</b> — Select one of the above agreements to regenerate<br>"
            "✨ &nbsp;<b>New Agreement</b> — Draft a completely new legal agreement<br>"
            "🔙 &nbsp;<b>Main Menu</b> — Return to the main options"
        ),
        "post_history_audio": (
            "Sir, how would you like to proceed? "
            "You may regenerate one of the existing agreements, "
            "or draft a completely new legal agreement."
        ),
        # ── Agreement type selection ───────────────────────────────────────────
        "ask_agreement_type": (
            "Understood, Sir. Please select the <b>type of agreement</b> you wish to create:<br><br>"
            "🏦 &nbsp;Account Opening Agreements<br>"
            "💻 &nbsp;Electronic Banking / Internet Banking Agreements<br>"
            "💱 &nbsp;Foreign Exchange (Forex) Agreement<br><br>"
            "Please type or speak the agreement type."
        ),
        "ask_agreement_type_audio": (
            "Understood Sir. Please specify the type of agreement you wish to create, "
            "such as Account Opening Agreements, Electronic Banking or Internet Banking Agreements, "
            "or Foreign Exchange Forex Agreement."
        ),
        # ── Party details ──────────────────────────────────────────────────────
        "ask_party_name": (
            "Noted, Sir — <b>{agreement_type}</b>.<br><br>"
            "Now, please provide the <b>name of the counterparty</b> "
            "(the second party in this agreement)."
        ),
        "ask_party_name_audio": (
            "Noted Sir. Now please provide the name of the counterparty "
            "in this agreement."
        ),
        "ask_value": (
            "Thank you, Sir. What is the <b>monetary value or duration</b> associated "
            "with this agreement?<br>"
            "<i>(e.g. ₹5,00,000 or 2 years or N/A if not applicable)</i>"
        ),
        "ask_value_audio": (
            "Thank you Sir. What is the monetary value or duration associated "
            "with this agreement? For example, five lakh rupees, or two years."
        ),
        # ── Confirmation before API call ───────────────────────────────────────
        "confirm_new_agreement": (
            "Sir, please review the agreement details before I proceed:<br><br>"
            "📋 &nbsp;<b>Agreement Type:</b> {detail2}<br>"
            "👤 &nbsp;<b>Counterparty:</b> {detail1}<br>"
            "💰 &nbsp;<b>Value / Duration:</b> {detail3}<br><br>"
            "⚠️ Shall I proceed to <b>generate this agreement</b>? "
            "Please confirm with <b>Yes</b> or <b>No</b>."
        ),
        "confirm_new_agreement_audio": (
            "Sir, please confirm the agreement details. "
            "Agreement type: {detail2}. "
            "Counterparty: {detail1}. "
            "Value or duration: {detail3}. "
            "Shall I proceed to generate this agreement?"
        ),
        "confirm_regen": (
            "Sir, I am about to <b>regenerate</b> the following agreement:<br><br>"
            "📋 &nbsp;<b>Type:</b> {doc_type}<br>"
            "👤 &nbsp;<b>Party:</b> {party}<br>"
            "📅 &nbsp;<b>Original Date:</b> {date}<br>"
            "💰 &nbsp;<b>Value:</b> {value}<br><br>"
            "⚠️ Do you confirm regeneration? Please respond <b>Yes</b> or <b>No</b>."
        ),
        "confirm_regen_audio": (
            "Sir, I am about to regenerate the {doc_type} with {party}. "
            "Do you confirm?"
        ),
        # ── Processing ─────────────────────────────────────────────────────────
        "generating": (
            "⚙️ Initiating document generation protocol, Sir. "
            "Communicating with the agreement engine. Please wait..."
        ),
        "generating_audio": (
            "Initiating document generation protocol Sir. Please wait."
        ),
        # ── Success ────────────────────────────────────────────────────────────
        "regen_success": (
            "✅ Sir, the agreement has been <b>successfully regenerated</b> "
            "and digitally notarised. Full details are shown below."
        ),
        "regen_success_audio": (
            "Sir, the agreement has been successfully regenerated and digitally notarised."
        ),
        "new_agreement_success": (
            "✅ Sir, your new legal agreement has been <b>generated and recorded</b> "
            "in the system. Please find the full details below."
        ),
        "new_agreement_success_audio": (
            "Sir, your new legal agreement has been generated and recorded in the system."
        ),
        # ── Verify flow ────────────────────────────────────────────────────────
        "ask_doc_id": (
            "Certainly, Sir. To verify a document, please provide the "
            "<b>Document ID</b> or <b>Reference Number</b> you wish to validate."
        ),
        "ask_doc_id_audio": (
            "Certainly Sir. Please provide the document ID or reference number "
            "you wish to validate."
        ),
        "verify_processing": (
            "🔍 Initiating document verification protocol, Sir. "
            "Cross-referencing with the secure ledger..."
        ),
        "verify_processing_audio": (
            "Initiating document verification Sir. Please wait."
        ),
        "verify_success": (
            "✅ Sir, the document <b>{doc_id}</b> has been <b>verified successfully</b>.<br><br>"
            "Please review the verification report below."
        ),
        "verify_success_audio": (
            "Sir, the document has been verified successfully."
        ),
        # ── Cancellation / back ────────────────────────────────────────────────
        "cancelled": (
            "Understood, Sir. The operation has been <b>cancelled</b>. "
            "Returning you to the main menu."
        ),
        "cancelled_audio": (
            "Understood Sir. The operation has been cancelled. Returning to main menu."
        ),
        # ── Clarification ──────────────────────────────────────────────────────
        "clarify": (
            "I beg your pardon, Sir. I did not fully understand your request.<br><br>"
            "Could you please clarify? You may say or type one of the following:<br>"
            "• &nbsp;<b>\"Generate Agreement\"</b> — to create a legal document<br>"
            "• &nbsp;<b>\"Verify Document\"</b> — to validate an agreement<br>"
            "• &nbsp;<b>\"View History\"</b> — to see past agreements<br>"
            "• &nbsp;<b>\"Hello\"</b> — to restart"
        ),
        "clarify_audio": (
            "I beg your pardon Sir. Could you clarify your request? "
            "You may say Generate Agreement, Verify Document, View History, or Hello to restart."
        ),
        # ── What next ──────────────────────────────────────────────────────────
        "what_next": (
            "Is there anything else I may assist you with, Sir?<br>"
            "You may choose another service or type <b>Main Menu</b> to return."
        ),
        "what_next_audio": (
            "Is there anything else I may assist you with Sir?"
        ),
    },

    # ══════════════════════════════════════════════════════════════════════════
    "हिंदी (Hindi)": {
        "greeting": (
            "नमस्ते, श्रीमान। मैं <b>जार्विस</b> हूँ — आपका AI कानूनी समझौता सहायक।<br><br>"
            "मैं निम्नलिखित सेवाओं में आपकी सहायता कर सकता हूँ:<br>"
            "⚖️ &nbsp;<b>कानूनी / बैंक समझौते बनाएं</b><br>"
            "🔍 &nbsp;<b>दस्तावेज़ सत्यापित करें</b><br>"
            "📋 &nbsp;<b>समझौता इतिहास देखें</b><br><br>"
            "आज मैं आपकी कैसे सेवा कर सकता हूँ?"
        ),
        "greeting_audio": (
            "नमस्ते श्रीमान। मैं जार्विस हूँ, आपका AI कानूनी समझौता सहायक। "
            "मैं कानूनी समझौते बनाने, दस्तावेज़ सत्यापित करने, "
            "या आपका इतिहास देखने में मदद कर सकता हूँ। आज कैसे मदद करूँ?"
        ),
        "main_menu": (
            "श्रीमान, कृपया एक विकल्प चुनें:<br>"
            "1️⃣ &nbsp;<b>समझौता बनाएं</b><br>"
            "2️⃣ &nbsp;<b>दस्तावेज़ सत्यापित करें</b><br>"
            "3️⃣ &nbsp;<b>समझौता इतिहास</b>"
        ),
        "main_menu_audio": (
            "श्रीमान, कृपया विकल्प चुनें। "
            "एक: समझौता बनाएं। दो: दस्तावेज़ सत्यापित करें। तीन: समझौता इतिहास।"
        ),
        "ask_name": (
            "बिल्कुल, श्रीमान। आगे बढ़ने से पहले, कृपया अपना <b>पूरा नाम</b> बताएं "
            "ताकि मैं आपके रिकॉर्ड प्राप्त कर सकूँ।"
        ),
        "ask_name_audio": "बिल्कुल श्रीमान। कृपया अपना पूरा नाम बताएं।",
        "fetching": "धन्यवाद, श्रीमान। <b>{name}</b> के रिकॉर्ड खोजे जा रहे हैं। कृपया प्रतीक्षा करें...",
        "fetching_audio": "धन्यवाद श्रीमान। {name} के रिकॉर्ड खोजे जा रहे हैं।",
        "history_found": "श्रीमान, <b>{name}</b> के लिए <b>{count}</b> दस्तावेज़ मिले। कृपया देखें:",
        "history_found_audio": "श्रीमान, {name} के लिए {count} दस्तावेज़ मिले।",
        "history_empty": "श्रीमान, <b>{name}</b> के लिए कोई रिकॉर्ड नहीं मिला। क्या आप नया समझौता बनाना चाहते हैं?",
        "history_empty_audio": "श्रीमान, {name} के लिए कोई रिकॉर्ड नहीं मिला।",
        "post_history": (
            "श्रीमान, आप कैसे आगे बढ़ना चाहते हैं?<br>"
            "🔄 &nbsp;<b>पुनः बनाएं</b> — पुराने समझौते को पुनः जनरेट करें<br>"
            "✨ &nbsp;<b>नया समझौता</b> — बिल्कुल नया समझौता बनाएं<br>"
            "🔙 &nbsp;<b>मुख्य मेनू</b>"
        ),
        "post_history_audio": "श्रीमान, पुराना पुनः बनाएं या नया समझौता बनाएं?",
        "ask_agreement_type": (
            "ठीक है, श्रीमान। कृपया <b>समझौते का प्रकार</b> बताएं:<br>"
            "खाता खोलने का समझौता, इलेक्ट्रॉनिक बैंकिंग / इंटरनेट बैंकिंग समझौता, "
            "विदेशी मुद्रा (फोरेक्स) समझौता।"
        ),
        "ask_agreement_type_audio": "ठीक है श्रीमान। कृपया समझौते का प्रकार बताएं।",
        "ask_party_name": "धन्यवाद, श्रीमान। अब कृपया <b>दूसरे पक्ष का नाम</b> बताएं।",
        "ask_party_name_audio": "धन्यवाद श्रीमान। दूसरे पक्ष का नाम बताएं।",
        "ask_value": "ठीक है, श्रीमान। इस समझौते की <b>राशि या अवधि</b> क्या है?",
        "ask_value_audio": "श्रीमान, इस समझौते की राशि या अवधि बताएं।",
        "confirm_new_agreement": (
            "श्रीमान, कृपया विवरण जांचें:<br>"
            "📋 &nbsp;<b>समझौता:</b> {detail2}<br>"
            "👤 &nbsp;<b>पक्ष:</b> {detail1}<br>"
            "💰 &nbsp;<b>राशि/अवधि:</b> {detail3}<br><br>"
            "⚠️ क्या मैं इसे जनरेट करूँ? <b>हाँ</b> या <b>नहीं</b> बोलें।"
        ),
        "confirm_new_agreement_audio": (
            "श्रीमान, समझौता {detail2}, पक्ष {detail1}, राशि {detail3}। "
            "क्या मैं आगे बढ़ूँ?"
        ),
        "confirm_regen": (
            "श्रीमान, मैं यह समझौता पुनः बनाने वाला हूँ:<br>"
            "📋 {doc_type} — {party} — {date}<br>"
            "⚠️ क्या आप पुष्टि करते हैं?"
        ),
        "confirm_regen_audio": "श्रीमान, {party} का {doc_type} पुनः बनाएं?",
        "generating": "⚙️ दस्तावेज़ निर्माण प्रारंभ हो रहा है, श्रीमान...",
        "generating_audio": "दस्तावेज़ निर्माण हो रहा है श्रीमान।",
        "regen_success": "✅ श्रीमान, समझौता <b>सफलतापूर्वक पुनः बनाया</b> गया। विवरण देखें:",
        "regen_success_audio": "श्रीमान, समझौता सफलतापूर्वक तैयार हो गया।",
        "new_agreement_success": "✅ श्रीमान, आपका नया समझौता <b>सफलतापूर्वक बन गया</b>। विवरण:",
        "new_agreement_success_audio": "श्रीमान, आपका नया समझौता तैयार हो गया।",
        "ask_doc_id": "बिल्कुल, श्रीमान। सत्यापन के लिए <b>दस्तावेज़ ID</b> या <b>संदर्भ संख्या</b> बताएं।",
        "ask_doc_id_audio": "श्रीमान, दस्तावेज़ ID या संदर्भ संख्या बताएं।",
        "verify_processing": "🔍 दस्तावेज़ सत्यापन हो रहा है, श्रीमान...",
        "verify_processing_audio": "दस्तावेज़ सत्यापन हो रहा है श्रीमान।",
        "verify_success": "✅ श्रीमान, दस्तावेज़ <b>{doc_id}</b> <b>सफलतापूर्वक सत्यापित</b> हुआ।",
        "verify_success_audio": "श्रीमान, दस्तावेज़ सफलतापूर्वक सत्यापित हुआ।",
        "cancelled": "समझ गया, श्रीमान। ऑपरेशन <b>रद्द</b> किया गया। मुख्य मेनू पर वापस।",
        "cancelled_audio": "समझ गया श्रीमान। ऑपरेशन रद्द किया गया।",
        "clarify": (
            "क्षमा करें, श्रीमान। मैं समझ नहीं पाया।<br>"
            "कृपया बताएं: <b>समझौता बनाएं</b>, <b>सत्यापित करें</b>, या <b>इतिहास देखें</b>।"
        ),
        "clarify_audio": "क्षमा करें श्रीमान, मैं समझ नहीं पाया। कृपया दोबारा बताएं।",
        "what_next": "श्रीमान, क्या कोई और सेवा चाहिए? <b>मुख्य मेनू</b> टाइप करें या नई सेवा चुनें।",
        "what_next_audio": "श्रीमान, क्या कोई और मदद चाहिए?",
    },

    # ══════════════════════════════════════════════════════════════════════════
    "मराठी (Marathi)": {
        "greeting": (
            "नमस्कार, साहेब। मी <b>जार्विस</b> आहे — तुमचा AI कायदेशीर करार सहायक।<br><br>"
            "मी खालील सेवांमध्ये मदत करू शकतो:<br>"
            "⚖️ &nbsp;<b>कायदेशीर / बँक करार तयार करा</b><br>"
            "🔍 &nbsp;<b>कागदपत्र सत्यापित करा</b><br>"
            "📋 &nbsp;<b>करार इतिहास पहा</b><br><br>"
            "आज मी तुमच्यासाठी काय करू?"
        ),
        "greeting_audio": (
            "नमस्कार साहेब। मी जार्विस आहे, तुमचा AI कायदेशीर करार सहायक। "
            "मी कायदेशीर करार तयार करणे, कागदपत्र सत्यापित करणे, "
            "किंवा इतिहास पाहण्यात मदत करू शकतो. आज काय करू?"
        ),
        "main_menu": (
            "साहेब, कृपया एक पर्याय निवडा:<br>"
            "1️⃣ &nbsp;<b>करार तयार करा</b><br>"
            "2️⃣ &nbsp;<b>कागदपत्र सत्यापित करा</b><br>"
            "3️⃣ &nbsp;<b>करार इतिहास</b>"
        ),
        "main_menu_audio": (
            "साहेब, पर्याय निवडा. एक: करार तयार करा. दोन: सत्यापित करा. तीन: इतिहास."
        ),
        "ask_name": (
            "नक्कीच, साहेब। पुढे जाण्यापूर्वी, कृपया तुमचे <b>पूर्ण नाव</b> सांगा "
            "म्हणजे मी तुमचे रेकॉर्ड मिळवू शकेन."
        ),
        "ask_name_audio": "नक्कीच साहेब, कृपया तुमचे पूर्ण नाव सांगा.",
        "fetching": "धन्यवाद, साहेब। <b>{name}</b> चे रेकॉर्ड शोधले जात आहेत. कृपया थांबा...",
        "fetching_audio": "धन्यवाद साहेब. {name} चे रेकॉर्ड शोधले जात आहेत.",
        "history_found": "साहेब, <b>{name}</b> साठी <b>{count}</b> करार सापडले. कृपया पाहा:",
        "history_found_audio": "साहेब, {name} साठी {count} करार सापडले.",
        "history_empty": "साहेब, <b>{name}</b> साठी कोणतेही रेकॉर्ड आढळले नाही. नवीन करार तयार करायचा आहे का?",
        "history_empty_audio": "साहेब, {name} साठी कोणतेही रेकॉर्ड नाही.",
        "post_history": (
            "साहेब, पुढे कसे जायचे?<br>"
            "🔄 &nbsp;<b>पुन्हा तयार करा</b> — जुना करार पुन्हा बनवा<br>"
            "✨ &nbsp;<b>नवीन करार</b> — नवीन कायदेशीर करार बनवा<br>"
            "🔙 &nbsp;<b>मुख्य मेनू</b>"
        ),
        "post_history_audio": "साहेब, जुना करार पुन्हा बनवायचा की नवीन करार?",
        "ask_agreement_type": (
            "ठीक आहे, साहेब। कृपया <b>करार प्रकार</b> सांगा:<br>"
            "खाते उघडण्याचा करार, इलेक्ट्रॉनिक बँकिंग / इंटरनेट बँकिंग करार, "
            "परकीय चलन (फोरेक्स) करार."
        ),
        "ask_agreement_type_audio": "ठीक आहे साहेब. कृपया करार प्रकार सांगा.",
        "ask_party_name": "धन्यवाद, साहेब। आता कृपया <b>दुसऱ्या पक्षाचे नाव</b> सांगा.",
        "ask_party_name_audio": "धन्यवाद साहेब. दुसऱ्या पक्षाचे नाव सांगा.",
        "ask_value": "ठीक आहे, साहेब। या कराराची <b>रक्कम किंवा कालावधी</b> काय आहे?",
        "ask_value_audio": "साहेब, कराराची रक्कम किंवा कालावधी सांगा.",
        "confirm_new_agreement": (
            "साहेब, कृपया तपशील तपासा:<br>"
            "📋 &nbsp;<b>करार:</b> {detail2}<br>"
            "👤 &nbsp;<b>पक्ष:</b> {detail1}<br>"
            "💰 &nbsp;<b>रक्कम/कालावधी:</b> {detail3}<br><br>"
            "⚠️ करार तयार करू का? <b>हो</b> किंवा <b>नाही</b> सांगा."
        ),
        "confirm_new_agreement_audio": (
            "साहेब, करार {detail2}, पक्ष {detail1}, रक्कम {detail3}. पुढे जाऊ का?"
        ),
        "confirm_regen": (
            "साहेब, मी हा करार पुन्हा तयार करणार आहे:<br>"
            "📋 {doc_type} — {party} — {date}<br>"
            "⚠️ तुम्ही पुष्टी करता का?"
        ),
        "confirm_regen_audio": "साहेब, {party} चा {doc_type} पुन्हा तयार करू का?",
        "generating": "⚙️ कागदपत्र निर्मिती सुरू आहे, साहेब...",
        "generating_audio": "कागदपत्र निर्मिती सुरू आहे साहेब.",
        "regen_success": "✅ साहेब, करार <b>यशस्वीरित्या पुन्हा तयार</b> झाला. तपशील पाहा:",
        "regen_success_audio": "साहेब, करार यशस्वीरित्या तयार झाला.",
        "new_agreement_success": "✅ साहेब, नवीन करार <b>यशस्वीरित्या तयार</b> झाला. तपशील:",
        "new_agreement_success_audio": "साहेब, नवीन करार यशस्वीरित्या तयार झाला.",
        "ask_doc_id": "नक्कीच, साहेब. सत्यापनासाठी <b>दस्तावेज ID</b> किंवा <b>संदर्भ क्रमांक</b> सांगा.",
        "ask_doc_id_audio": "साहेब, दस्तावेज ID किंवा संदर्भ क्रमांक सांगा.",
        "verify_processing": "🔍 कागदपत्र सत्यापन होत आहे, साहेब...",
        "verify_processing_audio": "कागदपत्र सत्यापन होत आहे साहेब.",
        "verify_success": "✅ साहेब, दस्तावेज <b>{doc_id}</b> <b>यशस्वीरित्या सत्यापित</b> झाला.",
        "verify_success_audio": "साहेब, दस्तावेज यशस्वीरित्या सत्यापित झाला.",
        "cancelled": "समजले, साहेब. ऑपरेशन <b>रद्द</b> केले. मुख्य मेनूवर परत.",
        "cancelled_audio": "समजले साहेब. ऑपरेशन रद्द केले.",
        "clarify": (
            "माफ करा, साहेब. मला समजले नाही.<br>"
            "कृपया सांगा: <b>करार तयार करा</b>, <b>सत्यापित करा</b>, किंवा <b>इतिहास पहा</b>."
        ),
        "clarify_audio": "माफ करा साहेब, समजले नाही. कृपया पुन्हा सांगा.",
        "what_next": "साहेब, आणखी काही मदत हवी आहे का? <b>मुख्य मेनू</b> टाइप करा किंवा नवीन सेवा निवडा.",
        "what_next_audio": "साहेब, आणखी काही मदत हवी आहे का?",
    },

    # ══════════════════════════════════════════════════════════════════════════
    "Deutsch (German)": {
        # ── Greeting ──────────────────────────────────────────────────────────
        "greeting": (
            "Guten Tag, mein Herr. Ich bin <b>DIA</b> — Ihr KI-Rechtsassistent.<br><br>"
            "Ich bin befugt, Ihnen bei folgenden Diensten zu helfen:<br>"
            "⚖️ &nbsp;<b>Rechts- / Bankverträge erstellen</b><br>"
            "🔍 &nbsp;<b>Dokumente verifizieren</b><br>"
            "📋 &nbsp;<b>Vertragshistorie abrufen</b><br><br>"
            "Wie kann ich Ihnen heute behilflich sein?"
        ),
        "greeting_audio": (
            "Guten Tag, mein Herr. Ich bin DIA, Ihr KI-Rechtsassistent. "
            "Ich kann Ihnen helfen, Rechtsverträge zu erstellen, Dokumente zu verifizieren "
            "oder Ihre Vertragshistorie abzurufen. Wie kann ich Ihnen heute helfen?"
        ),
        # ── Main menu ──────────────────────────────────────────────────────────
        "main_menu": (
            "Bitte wählen Sie eine der folgenden Optionen, mein Herr:<br>"
            "1️⃣ &nbsp;<b>Vertrag erstellen</b> — Neu erstellen oder aus Historie regenerieren<br>"
            "2️⃣ &nbsp;<b>Dokument verifizieren</b> — Bestehenden Vertrag prüfen<br>"
            "3️⃣ &nbsp;<b>Vertragshistorie</b> — Alle früheren Dokumente ansehen<br><br>"
            "Sie können Ihre Auswahl eingeben oder eine Schaltfläche unten wählen."
        ),
        "main_menu_audio": (
            "Bitte wählen Sie eine Option, mein Herr. "
            "Option 1: Vertrag erstellen. "
            "Option 2: Dokument verifizieren. "
            "Option 3: Vertragshistorie ansehen."
        ),
        # ── Identity ───────────────────────────────────────────────────────────
        "ask_name": (
            "Selbstverständlich, mein Herr. Bevor ich fortfahre, darf ich bitte Ihren "
            "<b>vollständigen Namen</b> erfahren, damit ich Ihre Unterlagen abrufen kann?"
        ),
        "ask_name_audio": (
            "Selbstverständlich, mein Herr. Darf ich bitte Ihren vollständigen Namen erfahren?"
        ),
        # ── Fetching history ───────────────────────────────────────────────────
        "fetching": (
            "Vielen Dank, mein Herr. Ich greife auf das sichere Dokumentenarchiv für "
            "<b>{name}</b> zu. Bitte warten Sie einen Moment..."
        ),
        "fetching_audio": (
            "Vielen Dank, mein Herr. Ich rufe das Archiv für {name} ab. Bitte warten."
        ),
        "history_found": (
            "Mein Herr, ich habe <b>{count}</b> Vertragsdatensatz/Datensätze für <b>{name}</b> gefunden. "
            "Bitte prüfen Sie die angezeigten Dokumente."
        ),
        "history_found_audio": (
            "Mein Herr, ich habe {count} Datensätze für {name} gefunden. Bitte prüfen Sie sie."
        ),
        "history_empty": (
            "Mein Herr, ich konnte keine Vertragsdaten für <b>{name}</b> finden. "
            "Möchten Sie stattdessen einen <b>neuen Vertrag erstellen</b>?"
        ),
        "history_empty_audio": (
            "Mein Herr, keine Datensätze für {name} gefunden. Möchten Sie einen neuen Vertrag erstellen?"
        ),
        # ── Post-history ───────────────────────────────────────────────────────
        "post_history": (
            "Mein Herr, wie möchten Sie fortfahren?<br><br>"
            "🔄 &nbsp;<b>Regenerieren</b> — Einen der obigen Verträge neu erstellen<br>"
            "✨ &nbsp;<b>Neuer Vertrag</b> — Einen völlig neuen Rechtsvertrag erstellen<br>"
            "🔙 &nbsp;<b>Hauptmenü</b> — Zu den Hauptoptionen zurückkehren"
        ),
        "post_history_audio": (
            "Mein Herr, wie möchten Sie fortfahren? "
            "Sie können einen bestehenden Vertrag neu erstellen oder einen neuen Vertrag anlegen."
        ),
        # ── Agreement type ─────────────────────────────────────────────────────
        "ask_agreement_type": (
            "Verstanden, mein Herr. Bitte wählen Sie die <b>Art des Vertrags</b>:<br><br>"
            "🏦 &nbsp;Kontoeröffnungsverträge<br>"
            "💻 &nbsp;Electronic Banking / Internet Banking Verträge<br>"
            "💱 &nbsp;Devisenhandel (Forex) Vertrag<br><br>"
            "Bitte geben Sie die Vertragsart ein oder sprechen Sie sie."
        ),
        "ask_agreement_type_audio": (
            "Verstanden, mein Herr. Bitte geben Sie die gewünschte Vertragsart an."
        ),
        # ── Party details ──────────────────────────────────────────────────────
        "ask_party_name": (
            "Notiert, mein Herr — <b>{agreement_type}</b>.<br><br>"
            "Bitte nennen Sie nun den <b>Namen der Gegenpartei</b> in diesem Vertrag."
        ),
        "ask_party_name_audio": (
            "Notiert, mein Herr. Bitte nennen Sie den Namen der Gegenpartei."
        ),
        "ask_value": (
            "Vielen Dank, mein Herr. Wie hoch ist der <b>Betrag oder die Laufzeit</b> dieses Vertrags?<br>"
            "<i>(z. B. 500.000 € oder 2 Jahre oder N/A)</i>"
        ),
        "ask_value_audio": (
            "Vielen Dank, mein Herr. Bitte nennen Sie den Betrag oder die Laufzeit des Vertrags."
        ),
        # ── Confirmation ───────────────────────────────────────────────────────
        "confirm_new_agreement": (
            "Mein Herr, bitte prüfen Sie die Vertragsdetails:<br><br>"
            "📋 &nbsp;<b>Vertragsart:</b> {detail2}<br>"
            "👤 &nbsp;<b>Gegenpartei:</b> {detail1}<br>"
            "💰 &nbsp;<b>Betrag / Laufzeit:</b> {detail3}<br><br>"
            "⚠️ Soll ich diesen Vertrag <b>erstellen</b>? Bitte bestätigen Sie mit <b>Ja</b> oder <b>Nein</b>."
        ),
        "confirm_new_agreement_audio": (
            "Mein Herr, bitte bestätigen Sie: Vertragsart {detail2}, Gegenpartei {detail1}, "
            "Betrag {detail3}. Soll ich fortfahren?"
        ),
        "confirm_regen": (
            "Mein Herr, ich werde folgenden Vertrag <b>neu erstellen</b>:<br><br>"
            "📋 &nbsp;<b>Typ:</b> {doc_type}<br>"
            "👤 &nbsp;<b>Partei:</b> {party}<br>"
            "📅 &nbsp;<b>Originaldatum:</b> {date}<br>"
            "💰 &nbsp;<b>Wert:</b> {value}<br><br>"
            "⚠️ Bestätigen Sie die Neuerstellung? Bitte antworten Sie mit <b>Ja</b> oder <b>Nein</b>."
        ),
        "confirm_regen_audio": (
            "Mein Herr, ich werde den Vertrag {doc_type} mit {party} neu erstellen. Bestätigen Sie?"
        ),
        # ── Processing ─────────────────────────────────────────────────────────
        "generating": (
            "⚙️ Dokument-Generierungsprotokoll wird gestartet, mein Herr. Bitte warten..."
        ),
        "generating_audio": "Dokument-Generierung gestartet, mein Herr. Bitte warten.",
        # ── Success ────────────────────────────────────────────────────────────
        "regen_success": (
            "✅ Mein Herr, der Vertrag wurde <b>erfolgreich neu erstellt</b> und digital beglaubigt. "
            "Die vollständigen Details finden Sie unten."
        ),
        "regen_success_audio": "Mein Herr, der Vertrag wurde erfolgreich neu erstellt und beglaubigt.",
        "new_agreement_success": (
            "✅ Mein Herr, Ihr neuer Rechtsvertrag wurde <b>erstellt und erfasst</b>. "
            "Die vollständigen Details finden Sie unten."
        ),
        "new_agreement_success_audio": "Mein Herr, Ihr neuer Vertrag wurde erstellt und erfasst.",
        # ── Verify flow ────────────────────────────────────────────────────────
        "ask_doc_id": (
            "Selbstverständlich, mein Herr. Um ein Dokument zu verifizieren, nennen Sie bitte "
            "die <b>Dokument-ID</b> oder <b>Referenznummer</b>."
        ),
        "ask_doc_id_audio": (
            "Selbstverständlich, mein Herr. Bitte nennen Sie die Dokument-ID oder Referenznummer."
        ),
        "verify_processing": (
            "🔍 Dokument-Verifizierungsprotokoll wird gestartet, mein Herr. "
            "Abgleich mit dem sicheren Register..."
        ),
        "verify_processing_audio": "Dokument-Verifizierung läuft, mein Herr. Bitte warten.",
        "verify_success": (
            "✅ Mein Herr, das Dokument <b>{doc_id}</b> wurde <b>erfolgreich verifiziert</b>.<br><br>"
            "Bitte prüfen Sie den Verifizierungsbericht unten."
        ),
        "verify_success_audio": "Mein Herr, das Dokument wurde erfolgreich verifiziert.",
        # ── Cancellation ───────────────────────────────────────────────────────
        "cancelled": (
            "Verstanden, mein Herr. Der Vorgang wurde <b>abgebrochen</b>. "
            "Sie werden zum Hauptmenü zurückgeleitet."
        ),
        "cancelled_audio": "Verstanden, mein Herr. Vorgang abgebrochen. Zurück zum Hauptmenü.",
        # ── Clarification ──────────────────────────────────────────────────────
        "clarify": (
            "Verzeihung, mein Herr. Ich habe Ihre Anfrage nicht vollständig verstanden.<br><br>"
            "Bitte wählen Sie: <b>Vertrag erstellen</b>, <b>Dokument verifizieren</b> "
            "oder <b>Vertragshistorie</b>."
        ),
        "clarify_audio": (
            "Verzeihung, mein Herr. Ich habe das nicht verstanden. Bitte wiederholen Sie."
        ),
        "what_next": (
            "Mein Herr, kann ich noch etwas für Sie tun? Geben Sie <b>Hauptmenü</b> ein "
            "oder wählen Sie einen neuen Dienst."
        ),
        "what_next_audio": "Mein Herr, kann ich noch etwas für Sie tun?",
    },

    # ══════════════════════════════════════════════════════════════════════════
    "普通话 (Mandarin)": {
        # ── Greeting ──────────────────────────────────────────────────────────
        "greeting": (
            "您好，先生。我是 <b>DIA</b> — 您的AI法律协议助手。<br><br>"
            "我已获授权为您提供以下服务：<br>"
            "⚖️ &nbsp;<b>生成法律 / 银行协议</b><br>"
            "🔍 &nbsp;<b>验证已生成的文件</b><br>"
            "📋 &nbsp;<b>查看协议历史记录</b><br><br>"
            "今天有什么我可以为您效劳的？"
        ),
        "greeting_audio": (
            "您好，先生。我是DIA，您的AI法律协议助手。"
            "我可以帮您生成法律或银行协议、验证文件，"
            "或查看您的协议历史记录。今天有什么需要我帮助的吗？"
        ),
        # ── Main menu ──────────────────────────────────────────────────────────
        "main_menu": (
            "先生，请选择以下选项之一：<br>"
            "1️⃣ &nbsp;<b>生成协议</b> — 新建或从历史记录重新生成<br>"
            "2️⃣ &nbsp;<b>验证文件</b> — 验证现有协议<br>"
            "3️⃣ &nbsp;<b>协议历史</b> — 查看所有过往文件<br><br>"
            "您可以输入您的选择或点击下方按钮。"
        ),
        "main_menu_audio": (
            "先生，请选择一个选项。"
            "选项一：生成协议。"
            "选项二：验证文件。"
            "选项三：查看协议历史。"
        ),
        # ── Identity ───────────────────────────────────────────────────────────
        "ask_name": (
            "当然，先生。在继续之前，能否请您告知您的<b>全名</b>，"
            "以便我从系统中检索您的记录？"
        ),
        "ask_name_audio": "当然，先生。请问您的全名是什么？",
        # ── Fetching history ───────────────────────────────────────────────────
        "fetching": (
            "谢谢您，先生。正在访问 <b>{name}</b> 的安全文件库。请稍候..."
        ),
        "fetching_audio": "谢谢您，先生。正在检索 {name} 的记录，请稍候。",
        "history_found": (
            "先生，我已检索到 <b>{name}</b> 名下的 <b>{count}</b> 份协议记录。请查阅下方文件。"
        ),
        "history_found_audio": "先生，已找到 {name} 的 {count} 份协议记录，请查看。",
        "history_empty": (
            "先生，系统中未找到 <b>{name}</b> 的任何协议记录。"
            "您是否希望<b>创建新协议</b>？"
        ),
        "history_empty_audio": "先生，未找到 {name} 的记录。是否创建新协议？",
        # ── Post-history ───────────────────────────────────────────────────────
        "post_history": (
            "先生，您希望如何继续？<br><br>"
            "🔄 &nbsp;<b>重新生成</b> — 选择以上某份协议重新生成<br>"
            "✨ &nbsp;<b>新建协议</b> — 起草全新的法律协议<br>"
            "🔙 &nbsp;<b>主菜单</b> — 返回主选项"
        ),
        "post_history_audio": "先生，您希望如何继续？可以重新生成旧协议，或起草全新协议。",
        # ── Agreement type ─────────────────────────────────────────────────────
        "ask_agreement_type": (
            "明白了，先生。请选择您希望创建的<b>协议类型</b>：<br><br>"
            "🏦 &nbsp;开户协议<br>"
            "💻 &nbsp;电子银行 / 网络银行协议<br>"
            "💱 &nbsp;外汇（Forex）协议<br><br>"
            "请输入或说出协议类型。"
        ),
        "ask_agreement_type_audio": "明白了，先生。请说明您希望创建的协议类型。",
        # ── Party details ──────────────────────────────────────────────────────
        "ask_party_name": (
            "已记录，先生 — <b>{agreement_type}</b>。<br><br>"
            "请提供本协议中<b>对方当事人的姓名</b>。"
        ),
        "ask_party_name_audio": "已记录，先生。请告知协议对方当事人的姓名。",
        "ask_value": (
            "谢谢您，先生。本协议涉及的<b>金额或期限</b>是多少？<br>"
            "<i>（例如：500,000元 或 2年 或 N/A）</i>"
        ),
        "ask_value_audio": "谢谢您，先生。请告知本协议的金额或期限。",
        # ── Confirmation ───────────────────────────────────────────────────────
        "confirm_new_agreement": (
            "先生，请核对以下协议详情：<br><br>"
            "📋 &nbsp;<b>协议类型：</b>{detail2}<br>"
            "👤 &nbsp;<b>对方当事人：</b>{detail1}<br>"
            "💰 &nbsp;<b>金额 / 期限：</b>{detail3}<br><br>"
            "⚠️ 是否<b>生成此协议</b>？请回复<b>是</b>或<b>否</b>。"
        ),
        "confirm_new_agreement_audio": (
            "先生，请确认协议详情：协议类型 {detail2}，对方当事人 {detail1}，金额 {detail3}。是否继续？"
        ),
        "confirm_regen": (
            "先生，我即将<b>重新生成</b>以下协议：<br><br>"
            "📋 &nbsp;<b>类型：</b>{doc_type}<br>"
            "👤 &nbsp;<b>当事人：</b>{party}<br>"
            "📅 &nbsp;<b>原始日期：</b>{date}<br>"
            "💰 &nbsp;<b>金额：</b>{value}<br><br>"
            "⚠️ 确认重新生成？请回复<b>是</b>或<b>否</b>。"
        ),
        "confirm_regen_audio": "先生，即将重新生成 {party} 的 {doc_type}。确认吗？",
        # ── Processing ─────────────────────────────────────────────────────────
        "generating": "⚙️ 正在启动文件生成程序，先生。请稍候...",
        "generating_audio": "正在启动文件生成程序，先生，请稍候。",
        # ── Success ────────────────────────────────────────────────────────────
        "regen_success": (
            "✅ 先生，协议已<b>成功重新生成</b>并经数字公证。详细信息如下。"
        ),
        "regen_success_audio": "先生，协议已成功重新生成并完成数字公证。",
        "new_agreement_success": (
            "✅ 先生，您的新法律协议已<b>生成并记录</b>在系统中。详细信息如下。"
        ),
        "new_agreement_success_audio": "先生，您的新法律协议已生成并记录在系统中。",
        # ── Verify flow ────────────────────────────────────────────────────────
        "ask_doc_id": (
            "当然，先生。若要验证文件，请提供您希望验证的<b>文件ID</b>或<b>参考编号</b>。"
        ),
        "ask_doc_id_audio": "当然，先生。请提供文件ID或参考编号。",
        "verify_processing": "🔍 正在启动文件验证程序，先生。交叉核验安全台账中...",
        "verify_processing_audio": "正在启动文件验证程序，先生，请稍候。",
        "verify_success": (
            "✅ 先生，文件 <b>{doc_id}</b> 已<b>成功验证</b>。<br><br>请查阅下方验证报告。"
        ),
        "verify_success_audio": "先生，文件已成功验证。",
        # ── Cancellation ───────────────────────────────────────────────────────
        "cancelled": "明白，先生。操作已<b>取消</b>。正在返回主菜单。",
        "cancelled_audio": "明白，先生。操作已取消，返回主菜单。",
        # ── Clarification ──────────────────────────────────────────────────────
        "clarify": (
            "抱歉，先生。我未能完全理解您的请求。<br><br>"
            "请选择：<b>生成协议</b>、<b>验证文件</b>或<b>查看历史</b>。"
        ),
        "clarify_audio": "抱歉，先生，我没有理解。请再说一次。",
        "what_next": (
            "先生，还有什么需要我效劳的吗？请输入<b>主菜单</b>或选择新服务。"
        ),
        "what_next_audio": "先生，还有什么需要我帮助的吗？",
    },
}


def get_response(key: str, language: str, **kwargs) -> str:
    """Get a chat response string in the specified language."""
    lang_responses = RESPONSES.get(language, RESPONSES["English"])
    template = lang_responses.get(key, RESPONSES["English"].get(key, f"[{key}]"))
    try:
        return template.format(**kwargs)
    except KeyError:
        return template


def get_audio_response(key: str, language: str, **kwargs) -> str:
    """Get the audio (plain text) version of a response."""
    audio_key = key + "_audio"
    lang_responses = RESPONSES.get(language, RESPONSES["English"])
    template = lang_responses.get(audio_key, RESPONSES["English"].get(audio_key, ""))
    if not template:
        # Fall back to chat version stripped of HTML
        template = get_response(key, language, **kwargs)
        import re
        template = re.sub(r'<[^>]+>', '', template)
        return template
    try:
        return template.format(**kwargs)
    except KeyError:
        return template


# ══════════════════════════════════════════════════════════════════════════════
#  Face-auth greeting messages (used in conversation.py after face recognition)
# ══════════════════════════════════════════════════════════════════════════════

FACE_WELCOME = {
    "English": (
        "Welcome back, <b>{name}</b>! I recognised you instantly. "
        "Great to have you here again."
    ),
    "हिंदी (Hindi)": (
        "स्वागत है, <b>{name}</b>! मैंने आपको तुरंत पहचान लिया। "
        "आपसे फिर मिलकर अच्छा लगा।"
    ),
    "मराठी (Marathi)": (
        "स्वागत आहे, <b>{name}</b>! मी तुम्हाला लगेच ओळखले. "
        "पुन्हा भेटून आनंद झाला."
    ),
    "Deutsch (German)": (
        "Willkommen zurück, <b>{name}</b>! Ich habe Sie sofort erkannt. "
        "Schön, Sie wieder hier zu haben."
    ),
    "普通话 (Mandarin)": (
        "欢迎回来，<b>{name}</b>！我立刻认出了您。"
        "很高兴再次见到您。"
    ),
}

FACE_WELCOME_AUDIO = {
    "English":          "Welcome back, {name}! I recognised you instantly.",
    "हिंदी (Hindi)":    "स्वागत है {name}! मैंने आपको तुरंत पहचान लिया।",
    "मराठी (Marathi)":  "स्वागत आहे {name}! मी तुम्हाला लगेच ओळखले.",
    "Deutsch (German)": "Willkommen zurück, {name}! Ich habe Sie sofort erkannt.",
    "普通话 (Mandarin)": "欢迎回来，{name}！我立刻认出了您。",
}

FACE_NEW_USER = {
    "English": (
        "Hello! I haven't seen your face before. "
        "Please tell me your name so I can remember you next time."
    ),
    "हिंदी (Hindi)": (
        "नमस्ते! मैं आपको पहले नहीं पहचानता। "
        "कृपया अपना नाम बताएं ताकि मैं अगली बार आपको याद रखूँ।"
    ),
    "मराठी (Marathi)": (
        "नमस्कार! मी तुम्हाला आधी पाहिले नाही. "
        "कृपया तुमचे नाव सांगा म्हणजे मी पुढच्या वेळी तुम्हाला ओळखेन."
    ),
    "Deutsch (German)": (
        "Hallo! Ich habe Sie noch nicht gesehen. "
        "Bitte nennen Sie mir Ihren Namen, damit ich Sie nächstes Mal erkennen kann."
    ),
    "普通话 (Mandarin)": (
        "您好！我以前没有见过您。"
        "请告诉我您的名字，这样下次我就能认出您了。"
    ),
}

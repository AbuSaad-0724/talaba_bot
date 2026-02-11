// DARSLIKLAR MA'LUMOTLAR BAZASI
const libraryData = {
    mathematics: {
        title: "Matematika",
        icon: "📐",
        gradient: "linear-gradient(135deg, #667eea, #764ba2)",
        category: "exact",
        levels: {
            beginner: {
                name: "Boshlang'ich matematika",
                materials: [
                    { type: "video", title: "Arifmetika asoslari", duration: "45 min", url: "#" },
                    { type: "pdf", title: "Sonlar va amallar", pages: 120, url: "#" },
                    { type: "audio", title: "Ko'paytirish jadvali", duration: "20 min", url: "#" },
                    { type: "video", title: "Kasrlar bilan ishlash", duration: "35 min", url: "#" },
                    { type: "pdf", title: "Geometriya asoslari", pages: 80, url: "#" }
                ]
            },
            intermediate: {
                name: "O'rta matematika",
                materials: [
                    { type: "video", title: "Algebra asoslari", duration: "60 min", url: "#" },
                    { type: "pdf", title: "Tenglamalar va tengsizliklar", pages: 150, url: "#" },
                    { type: "video", title: "Funksiyalar", duration: "50 min", url: "#" },
                    { type: "pdf", title: "Trigonometriya", pages: 100, url: "#" },
                    { type: "video", title: "Logarifmlar", duration: "40 min", url: "#" }
                ]
            },
            advanced: {
                name: "Oliy matematika",
                materials: [
                    { type: "video", title: "Limitlar va uzluksizlik", duration: "70 min", url: "#" },
                    { type: "pdf", title: "Hosilalar", pages: 180, url: "#" },
                    { type: "video", title: "Integrallar", duration: "65 min", url: "#" },
                    { type: "pdf", title: "Differensial tenglamalar", pages: 200, url: "#" },
                    { type: "video", title: "Chiziqli algebra", duration: "55 min", url: "#" }
                ]
            }
        }
    },

    physics: {
        title: "Fizika",
        icon: "⚛️",
        gradient: "linear-gradient(135deg, #4facfe, #00f2fe)",
        category: "exact",
        levels: {
            beginner: {
                name: "Boshlang'ich fizika",
                materials: [
                    { type: "video", title: "Mexanika asoslari", duration: "50 min", url: "#" },
                    { type: "pdf", title: "Harakat va kuch", pages: 110, url: "#" },
                    { type: "video", title: "Energiya va quvvat", duration: "40 min", url: "#" },
                    { type: "pdf", title: "Issiqlik va temperatura", pages: 90, url: "#" }
                ]
            },
            intermediate: {
                name: "O'rta fizika",
                materials: [
                    { type: "video", title: "Elektr va magnetizm", duration: "65 min", url: "#" },
                    { type: "pdf", title: "Optika", pages: 130, url: "#" },
                    { type: "video", title: "To'lqinlar va tebranishlar", duration: "55 min", url: "#" },
                    { type: "pdf", title: "Molekulyar fizika", pages: 140, url: "#" }
                ]
            },
            advanced: {
                name: "Oliy fizika",
                materials: [
                    { type: "video", title: "Kvant mexanikasi", duration: "75 min", url: "#" },
                    { type: "pdf", title: "Atom va yadro fizikasi", pages: 190, url: "#" },
                    { type: "video", title: "Nisbiylik nazariyasi", duration: "60 min", url: "#" },
                    { type: "pdf", title: "Zarralar fizikasi", pages: 170, url: "#" }
                ]
            }
        }
    },

    chemistry: {
        title: "Kimyo",
        icon: "🧪",
        gradient: "linear-gradient(135deg, #43e97b, #38f9d7)",
        category: "exact",
        levels: {
            beginner: {
                name: "Umumiy kimyo",
                materials: [
                    { type: "video", title: "Atomlar va molekulalar", duration: "45 min", url: "#" },
                    { type: "pdf", title: "Davriy jadval", pages: 100, url: "#" },
                    { type: "video", title: "Kimyoviy bog'lanishlar", duration: "50 min", url: "#" },
                    { type: "pdf", title: "Kimyoviy reaksiyalar", pages: 120, url: "#" }
                ]
            },
            intermediate: {
                name: "Noorganik kimyo",
                materials: [
                    { type: "video", title: "Metallar va nometallar", duration: "55 min", url: "#" },
                    { type: "pdf", title: "Kislotalar va asoslar", pages: 110, url: "#" },
                    { type: "video", title: "Oksidlanish-qaytarilish", duration: "48 min", url: "#" },
                    { type: "pdf", title: "Elektrolitlar", pages: 95, url: "#" }
                ]
            },
            advanced: {
                name: "Organik kimyo",
                materials: [
                    { type: "video", title: "Uglevodorodlar", duration: "60 min", url: "#" },
                    { type: "pdf", title: "Funksional guruhlar", pages: 150, url: "#" },
                    { type: "video", title: "Polimerlar", duration: "52 min", url: "#" },
                    { type: "pdf", title: "Biokimyo asoslari", pages: 140, url: "#" }
                ]
            }
        }
    },

    english: {
        title: "Ingliz tili",
        icon: "🇬🇧",
        gradient: "linear-gradient(135deg, #fa709a, #fee140)",
        category: "languages",
        levels: {
            beginner: {
                name: "A1-A2 (Boshlang'ich)",
                materials: [
                    { type: "audio", title: "Alfabet va talaffuz", duration: "30 min", url: "#" },
                    { type: "pdf", title: "Oddiy grammatika", pages: 80, url: "#" },
                    { type: "video", title: "Kundalik so'zlar", duration: "40 min", url: "#" },
                    { type: "audio", title: "Suhbat amaliyoti", duration: "35 min", url: "#" },
                    { type: "pdf", title: "1000 ta asosiy so'z", pages: 60, url: "#" }
                ]
            },
            intermediate: {
                name: "B1-B2 (O'rta)",
                materials: [
                    { type: "video", title: "Grammatika chuqurlashtirilgan", duration: "55 min", url: "#" },
                    { type: "pdf", title: "Idiomalar va iboralar", pages: 120, url: "#" },
                    { type: "audio", title: "Tinglab tushunish", duration: "45 min", url: "#" },
                    { type: "video", title: "Business English", duration: "50 min", url: "#" },
                    { type: "pdf", title: "Essay yozish", pages: 90, url: "#" }
                ]
            },
            advanced: {
                name: "C1-C2 (Yuqori)",
                materials: [
                    { type: "video", title: "Academic English", duration: "65 min", url: "#" },
                    { type: "pdf", title: "Murakkab grammatika", pages: 150, url: "#" },
                    { type: "audio", title: "Native speakers bilan suhbat", duration: "60 min", url: "#" },
                    { type: "video", title: "IELTS/TOEFL tayyorgarlik", duration: "70 min", url: "#" },
                    { type: "pdf", title: "Adabiy matnlar tahlili", pages: 130, url: "#" }
                ]
            }
        }
    },

    russian: {
        title: "Rus tili",
        icon: "🇷🇺",
        gradient: "linear-gradient(135deg, #f093fb, #f5576c)",
        category: "languages",
        levels: {
            beginner: {
                name: "Boshlang'ich",
                materials: [
                    { type: "audio", title: "Alifbo va talaffuz", duration: "35 min", url: "#" },
                    { type: "pdf", title: "Oddiy grammatika", pages: 85, url: "#" },
                    { type: "video", title: "Kundalik suhbatlar", duration: "42 min", url: "#" },
                    { type: "pdf", title: "Asosiy so'zlar", pages: 70, url: "#" }
                ]
            },
            intermediate: {
                name: "O'rta",
                materials: [
                    { type: "video", title: "Grammatika chuqurlashtirilgan", duration: "58 min", url: "#" },
                    { type: "pdf", title: "Kelishiklar tizimi", pages: 110, url: "#" },
                    { type: "audio", title: "Tinglab tushunish", duration: "48 min", url: "#" },
                    { type: "video", title: "Rasmiy uslub", duration: "45 min", url: "#" }
                ]
            },
            advanced: {
                name: "Yuqori",
                materials: [
                    { type: "video", title: "Adabiy rus tili", duration: "62 min", url: "#" },
                    { type: "pdf", title: "Murakkab sintaksis", pages: 140, url: "#" },
                    { type: "audio", title: "Klassik adabiyot", duration: "55 min", url: "#" },
                    { type: "pdf", title: "Ilmiy uslub", pages: 120, url: "#" }
                ]
            }
        }
    },

    worldHistory: {
        title: "Jahon tarixi",
        icon: "🌍",
        gradient: "linear-gradient(135deg, #ff9a9e, #fecfef)",
        category: "humanities",
        levels: {
            ancient: {
                name: "Qadimgi dunyo",
                materials: [
                    { type: "video", title: "Qadimgi Misr", duration: "50 min", url: "#" },
                    { type: "pdf", title: "Mesopotamiya sivilizatsiyalari", pages: 130, url: "#" },
                    { type: "video", title: "Qadimgi Yunoniston", duration: "55 min", url: "#" },
                    { type: "pdf", title: "Rim imperiyasi", pages: 150, url: "#" }
                ]
            },
            medieval: {
                name: "O'rta asrlar",
                materials: [
                    { type: "video", title: "Feodalizm davri", duration: "48 min", url: "#" },
                    { type: "pdf", title: "Islom sivilizatsiyasi", pages: 140, url: "#" },
                    { type: "video", title: "Uyg'onish davri", duration: "52 min", url: "#" },
                    { type: "pdf", title: "Buyuk geografik kashfiyotlar", pages: 120, url: "#" }
                ]
            },
            modern: {
                name: "Zamonaviy tarix",
                materials: [
                    { type: "video", title: "Sanoat inqilobi", duration: "58 min", url: "#" },
                    { type: "pdf", title: "Jahon urushlar", pages: 180, url: "#" },
                    { type: "video", title: "Sovuq urush", duration: "60 min", url: "#" },
                    { type: "pdf", title: "XXI asr globallashuvi", pages: 160, url: "#" }
                ]
            }
        }
    },

    uzbekistanHistory: {
        title: "O'zbekiston tarixi",
        icon: "🇺🇿",
        gradient: "linear-gradient(135deg, #a8edea, #fed6e3)",
        category: "humanities",
        levels: {
            ancient: {
                name: "Qadimgi O'zbekiston",
                materials: [
                    { type: "video", title: "Baqtriya va Sug'd", duration: "45 min", url: "#" },
                    { type: "pdf", title: "Xorazm sivilizatsiyasi", pages: 110, url: "#" },
                    { type: "video", title: "Buyuk Ipak yo'li", duration: "50 min", url: "#" },
                    { type: "pdf", title: "Qadimgi shaharlar", pages: 95, url: "#" }
                ]
            },
            independence: {
                name: "Mustaqillik davri",
                materials: [
                    { type: "video", title: "Mustaqillik e'lon qilinishi", duration: "40 min", url: "#" },
                    { type: "pdf", title: "Konstitutsiya asoslari", pages: 80, url: "#" },
                    { type: "video", title: "Iqtisodiy islohotlar", duration: "48 min", url: "#" },
                    { type: "pdf", title: "Demokratik jamiyat qurish", pages: 100, url: "#" }
                ]
            },
            modern: {
                name: "Zamonaviy O'zbekiston",
                materials: [
                    { type: "video", title: "Yangi O'zbekiston strategiyasi", duration: "52 min", url: "#" },
                    { type: "pdf", title: "Raqamli iqtisodiyot", pages: 120, url: "#" },
                    { type: "video", title: "Xalqaro hamkorlik", duration: "45 min", url: "#" },
                    { type: "pdf", title: "Ta'lim islohotlari", pages: 90, url: "#" }
                ]
            }
        }
    }
};

// Export for use in main app
if (typeof module !== 'undefined' && module.exports) {
    module.exports = libraryData;
}

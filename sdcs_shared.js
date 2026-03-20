// ════════════════════════════════════════════════════════════════════
// sdcs_shared.js — shared constants and functions
// Loaded by index.html and sdcs_campaign_v1.0.html
// Edit here; changes apply to both viewers automatically.
// DO NOT define UI_SCALE, map, or state variables here.
// ════════════════════════════════════════════════════════════════════

const CAMPAIGN_GEODATA = {
  bases: {
    189: [
      // Persian Gulf — E=pos_u-fe, N=pos_v-fn, fe=75756 fn=-2894933 lon0=57 (persiangulf.js)
      {id:1,  name:'Abu Musa Island',      lat:25.875991, lon:55.032918},
      {id:2,  name:'Bandar Abbas Intl',    lat:27.217687, lon:56.378962},
      {id:3,  name:'Bandar Lengeh',        lat:26.532264, lon:54.824667},
      {id:5,  name:'Dubai Intl',           lat:25.256376, lon:55.365261},
      {id:7,  name:'Fujairah Intl',        lat:25.110940, lon:56.327351},
      {id:8,  name:'Tunb Island AFB',      lat:26.258888, lon:55.315782},
      {id:10, name:'Khasab',               lat:26.169826, lon:56.240170},
      {id:11, name:'Lar',                  lat:27.674732, lon:54.383145},
      {id:13, name:'Qeshm Island',         lat:26.754669, lon:55.902384},
      {id:15, name:'Sirri Island',         lat:25.909603, lon:54.539254},
      {id:16, name:'Tunb Kochak',          lat:26.243322, lon:55.145568},
      {id:23, name:'Al-Bateen',            lat:24.428077, lon:54.458580},
      {id:24, name:'Kish Intl',            lat:26.528148, lon:53.981049},
      {id:25, name:'Al Ain Intl',          lat:24.261428, lon:55.609245},
      {id:26, name:'Lavan Island',         lat:26.811108, lon:53.353293},
      {id:27, name:'Jiroft',               lat:28.723517, lon:57.675095},
      {id:28, name:'Ras Al Khaimah Intl',  lat:25.613494, lon:55.938797},
      {id:29, name:'Liwa AFB',             lat:23.650775, lon:53.824429},
    ],
    190: [
      {id:12, name:'Anapa-Vityazevo', lat:45.004999, lon:37.343321},
      {id:16, name:'Maykop-Khanskaya', lat:44.681441, lon:40.030793},
      {id:18, name:'Sochi-Adler', lat:43.444500, lon:39.936706},
      {id:20, name:'Sukhumi-Babushara', lat:42.861280, lon:41.120683},
      {id:24, name:'Kobuleti', lat:41.930129, lon:41.859032},
      {id:25, name:'Kutaisi', lat:42.177850, lon:42.477044},
      {id:26, name:'Mineralnye Vody', lat:44.228123, lon:43.076812},
      {id:27, name:'Nalchik', lat:43.514288, lon:43.632140},
      {id:28, name:'Mozdok', lat:43.792035, lon:44.601546},
      {id:31, name:'Vaziani', lat:41.629347, lon:45.023104},
      {id:32, name:'Beslan', lat:43.206026, lon:44.601557},
    ],
    192: [
      // Germany — E=pos_u-fe, N=pos_v-fn, fe=35427.62 fn=-6061633.128 lon0=21 (germanycw.js)
      {id:1,   name:'Wittstock',    lat:53.202366, lon:12.522966},
      {id:5,   name:'Bremen',       lat:53.046937, lon:8.788165},
      {id:11,  name:'Fassberg',     lat:52.919424, lon:10.184779},
      {id:16,  name:'Gutersloh',    lat:51.922801, lon:8.303927},
      {id:17,  name:'Hamburg',      lat:53.626841, lon:9.981270},
      {id:20,  name:'Laage',        lat:53.918052, lon:12.279390},
      {id:27,  name:'Stendal',      lat:52.629081, lon:11.819845},
      {id:29,  name:'Tempelhof',    lat:52.471066, lon:13.404300},
      {id:101, name:'Sperenberg',   lat:52.136914, lon:13.305948},
      {id:107, name:'Braunschweig', lat:52.319081, lon:10.553895},
      {id:140, name:'Hasselfelde',  lat:51.705391, lon:10.878666},
      {id:154, name:'Fritzlar',     lat:51.114606, lon:9.285759},
      {id:159, name:'Giebelstadt',  lat:49.647899, lon:9.964686},
      {id:160, name:'Schweinfurt',  lat:50.048850, lon:10.169632},
      {id:161, name:'Haina',        lat:50.991661, lon:10.479535},
      {id:163, name:'Frankfurt',    lat:50.040426, lon:8.567208},
      {id:165, name:'Ramstein',     lat:49.436889, lon:7.599888},
      {id:166, name:'Fulda',        lat:50.539909, lon:9.642956},
    ],
    193: [
      {id:12, name:'Anapa-Vityazevo', lat:45.004999, lon:37.343321},
      {id:16, name:'Maykop-Khanskaya', lat:44.681441, lon:40.030793},
      {id:18, name:'Sochi-Adler', lat:43.444500, lon:39.936706},
      {id:20, name:'Sukhumi-Babushara', lat:42.861280, lon:41.120683},
      {id:24, name:'Kobuleti', lat:41.930129, lon:41.859032},
      {id:25, name:'Kutaisi', lat:42.177850, lon:42.477044},
      {id:26, name:'Mineralnye Vody', lat:44.228123, lon:43.076812},
      {id:27, name:'Nalchik', lat:43.514288, lon:43.632140},
      {id:28, name:'Mozdok', lat:43.792035, lon:44.601546},
      {id:31, name:'Vaziani', lat:41.629347, lon:45.023104},
      {id:32, name:'Beslan', lat:43.206026, lon:44.601557},
    ],
    185: [
      // Syria — E=pos_u-fe, N=pos_v-fn, fe=282801 fn=-3879866 lon0=39 (syria.js)
      {name:'Abu al-Duhur',             lat:35.732306, lon:37.104128},
      {name:'An Nasiriyah',             lat:33.918607, lon:36.865840},
      {name:'Beirut-Rafic Hariri',      lat:33.827268, lon:35.487687},
      {name:'Damascus',                 lat:33.425508, lon:36.518512},
      {name:'Gaziantep',                lat:36.948128, lon:37.478344},
      {name:'Hama',                     lat:35.118044, lon:36.712379},
      {name:'Hatay',                    lat:36.362320, lon:36.287422},
      {name:'King Hussein Air College', lat:32.356680, lon:36.259855},
      {name:'Bassel Al-Assad',          lat:35.401670, lon:35.950384},
      {name:'Minakh',                   lat:36.521376, lon:37.041337},
      {name:'Ramat David',              lat:32.666411, lon:35.184166},
      {name:'Kuweires',                 lat:36.187494, lon:37.581495},
      {name:'Rene Mouawad',             lat:34.589300, lon:36.011449},
      {name:'Tiyas',                    lat:34.522629, lon:37.630123},
      {name:'Ben Gurion',               lat:32.006079, lon:34.882423},
    ],
  },
  objectives: {
    189: [
      {code:'BN95', name:'BN95 Crossroad',    lat:24.894586, lon:54.921065},
      {code:'BP56', name:'Sirri Island',       lat:25.908340, lon:54.530664},
      {code:'BQ36', name:'BQ36 Crossroad',    lat:26.774510, lon:54.369816},
      {code:'BQ84', name:'Bandar Lengeh',     lat:26.565583, lon:54.826352},
      {code:'BR31', name:'Bastak',             lat:27.200223, lon:54.371855},
      {code:'CN39', name:'Dubai Intl',         lat:25.253331, lon:55.366117},
      {code:'CN46', name:'Al Lisalli',         lat:24.952641, lon:55.486649},
      {code:'CN62', name:'CN63 Crossroad',    lat:24.673410, lon:55.666420},
      {code:'CN86', name:'Nazwa',              lat:24.996583, lon:55.858238},
      {code:'CN89', name:'Al Dhaid',           lat:25.284455, lon:55.888752},
      {code:'CP52', name:'Umm Al Quwain',     lat:25.545655, lon:55.593264},
      {code:'CP93', name:'Ras Al Khaimah Intl',lat:25.602507, lon:55.965441},
      {code:'CQ10', name:'Tunb Kochak',       lat:26.243601, lon:55.149455},
      {code:'CQ34', name:'Basa\'idu',         lat:26.617697, lon:55.314380},
      {code:'CQ37', name:'Gavmiri',            lat:26.908218, lon:55.299034},
      {code:'CQ95', name:'Qeshm Island',      lat:26.742067, lon:55.914411},
      {code:'CR43', name:'CR43 Point',        lat:27.444650, lon:55.445931},
      {code:'CR80', name:'Gachin Bala',       lat:27.135967, lon:55.852953},
      {code:'DN37', name:'Fujairah Intl',     lat:25.115684, lon:56.330025},
      {code:'DN44', name:'Al Wadiyat',        lat:24.793792, lon:56.412421},
      {code:'DP06', name:'Al Rams',           lat:25.875238, lon:56.053201},
      {code:'DP23', name:'Dibba Al-Hisn',     lat:25.615256, lon:56.289403},
      {code:'DP29', name:'Khasab',             lat:26.182145, lon:56.248753},
      {code:'DP30', name:'Al Hutain',         lat:25.378635, lon:56.353067},
      {code:'DQ28', name:'Baharestan',        lat:26.950227, lon:56.214559},
      {code:'DQ89', name:'DQ89',               lat:27.100412, lon:56.876503},
      {code:'DR31', name:'Bandar Abbas Intl', lat:27.242774, lon:56.331222},
      {code:'EQ06', name:'EQ06 Harbour',      lat:26.820129, lon:57.076482},
      {code:'YK87', name:'YK87',               lat:26.895713, lon:53.841874},
      {code:'YK93', name:'Kish Intl',         lat:26.529966, lon:53.978322},
    ],
    190: [
      {code:'EJ08', name:'Tuapse', lat:44.117246, lon:39.113328},
      {code:'EJ36', name:'Lazarevskoe', lat:43.934838, lon:39.379293},
      {code:'EJ53', name:'Sochi', lat:43.652392, lon:39.708904},
      {code:'FH18', name:'Bzyb\'', lat:43.209058, lon:40.350090},
      {code:'FH66', name:'Sukhumi', lat:43.034720, lon:41.000470},
      {code:'FJ76', name:'Kobu-Bashi', lat:43.954684, lon:41.238555},
      {code:'FK01', name:'Abadzehskaya', lat:44.367608, lon:40.267558},
      {code:'FK34', name:'FK34 Crossroads', lat:44.652239, lon:40.667171},
      {code:'FK50', name:'Kaladzhinskaya', lat:44.270526, lon:40.914715},
      {code:'GG34', name:'Kobuleti', lat:41.937602, lon:41.837615},
      {code:'GG48', name:'Senaki', lat:42.264177, lon:41.933297},
      {code:'GH03', name:'Ochamchira', lat:42.734439, lon:41.511506},
      {code:'GH31', name:'Zugdidi', lat:42.526076, lon:41.846322},
      {code:'GJ35', name:'Karachaevsk', lat:43.802402, lon:41.905903},
      {code:'KQ60', name:'Cherkessk', lat:44.225292, lon:42.050075},
      {code:'LM87', name:'Jvari Pass', lat:42.186831, lon:43.600264},
      {code:'LN40', name:'Ambrolauri', lat:42.499534, lon:43.143725},
      {code:'LP06', name:'Uchkeken', lat:43.948024, lon:42.504086},
      {code:'LP56', name:'Zalukokoazhe', lat:43.894998, lon:43.195561},
      {code:'LP79', name:'Georgievsk', lat:44.154046, lon:43.455710},
      {code:'LP91', name:'Nalchik', lat:43.503836, lon:43.638994},
      {code:'MM19', name:'Didi-Gupta', lat:42.368958, lon:43.923225},
      {code:'MM79', name:'Nigniy Pasanauri', lat:42.368667, lon:44.678232},
      {code:'MN12', name:'Verhniy Zaramag', lat:42.676914, lon:43.975124},
      {code:'MN39', name:'Elhotovo', lat:43.328135, lon:44.206349},
      {code:'MN62', name:'Darial Pass', lat:42.686498, lon:44.626543},
      {code:'MP04', name:'Lesnoe', lat:43.792241, lon:43.827566},
      {code:'MP23', name:'Mayskiy', lat:43.620669, lon:44.092834},
      {code:'MP61', name:'Malgobek', lat:43.512859, lon:44.586159},
      {code:'MP74', name:'Mozdok', lat:43.751921, lon:44.623475},
    ],
    192: [
      {code:'MA74', name:'Frankfurt',                   lat:50.076427, lon:8.619346},
      {code:'MA89', name:'Giessen',                     lat:50.536438, lon:8.728838},
      {code:'MB55', name:'Erndtebrück',                 lat:51.007181, lon:8.319682},
      {code:'MC30', name:'Soest',                       lat:51.535518, lon:8.047201},
      {code:'MC82', name:'Paderborn',                   lat:51.720022, lon:8.734598},
      {code:'NA84', name:'Schweinfurt',                 lat:50.060676, lon:10.149793},
      {code:'NB16', name:'Fritzlar',                    lat:51.110896, lon:9.278866},
      {code:'NB40', name:'Fulda',                       lat:50.555476, lon:9.676734},
      {code:'NC34', name:'Hotzwinden',                  lat:51.845708, lon:9.490928},
      {code:'NC61', name:'Gottingen',                   lat:51.545189, lon:9.935468},
      {code:'ND01', name:'Stolzenau',                   lat:52.520872, lon:9.053315},
      {code:'ND50', name:'Hannover',                    lat:52.365541, lon:9.760733},
      {code:'ND76', name:'Fassberg',                    lat:52.941502, lon:10.151208},
      {code:'NE63', name:'Hamburg',                     lat:53.576353, lon:9.959363},
      {code:'PB20', name:'Meiningen',                   lat:50.613622, lon:10.799439},
      {code:'PB39', name:'Obermehler Schlotheim',       lat:51.359782, lon:10.883468},
      {code:'PB65', name:'Weimar',                      lat:50.987947, lon:11.353204},
      {code:'PC23', name:'Hasselfelde',                 lat:51.716660, lon:10.855824},
      {code:'PC87', name:'Magdeburg',                   lat:52.138781, lon:11.650490},
      {code:'PD45', name:'Salzwedel',                   lat:52.864029, lon:11.148414},
      {code:'PD93', name:'Stendal',                     lat:52.630378, lon:11.845860},
      {code:'PE41', name:'Hagenow',                     lat:53.392159, lon:11.239200},
      {code:'QC00', name:'Halle',                       lat:51.483552, lon:11.978611},
      {code:'UT34', name:'Lutherstadt Wittenberg',      lat:51.860635, lon:12.650354},
      {code:'UU39', name:'Wittstock',                   lat:53.205885, lon:12.530343},
      {code:'UU81', name:'Tempelhof',                   lat:52.515797, lon:13.370192},
    ],
    193: [
      {code:'EJ08', name:'Tuapse', lat:44.117246, lon:39.113328},
      {code:'EJ36', name:'Lazarevskoe', lat:43.934838, lon:39.379293},
      {code:'EJ53', name:'Sochi', lat:43.652392, lon:39.708904},
      {code:'FH18', name:'Bzyb\'', lat:43.209058, lon:40.350090},
      {code:'FH66', name:'Sukhumi', lat:43.034720, lon:41.000470},
      {code:'FJ76', name:'Kobu-Bashi', lat:43.954684, lon:41.238555},
      {code:'FK01', name:'Abadzehskaya', lat:44.367608, lon:40.267558},
      {code:'FK34', name:'FK34 Crossroads', lat:44.652239, lon:40.667171},
      {code:'FK50', name:'Kaladzhinskaya', lat:44.270526, lon:40.914715},
      {code:'GG34', name:'Kobuleti', lat:41.937602, lon:41.837615},
      {code:'GG48', name:'Senaki', lat:42.264177, lon:41.933297},
      {code:'GH03', name:'Ochamchira', lat:42.734439, lon:41.511506},
      {code:'GH31', name:'Zugdidi', lat:42.526076, lon:41.846322},
      {code:'GJ35', name:'Karachaevsk', lat:43.802402, lon:41.905903},
      {code:'KQ60', name:'Cherkessk', lat:44.225292, lon:42.050075},
      {code:'LM87', name:'Jvari Pass', lat:42.186831, lon:43.600264},
      {code:'LN40', name:'Ambrolauri', lat:42.499534, lon:43.143725},
      {code:'LP06', name:'Uchkeken', lat:43.948024, lon:42.504086},
      {code:'LP56', name:'Zalukokoazhe', lat:43.894998, lon:43.195561},
      {code:'LP79', name:'Georgievsk', lat:44.154046, lon:43.455710},
      {code:'LP91', name:'Nalchik', lat:43.503836, lon:43.638994},
      {code:'MM19', name:'Didi-Gupta', lat:42.368958, lon:43.923225},
      {code:'MM79', name:'Nigniy Pasanauri', lat:42.368667, lon:44.678232},
      {code:'MN12', name:'Verhniy Zaramag', lat:42.676914, lon:43.975124},
      {code:'MN39', name:'Elhotovo', lat:43.328135, lon:44.206349},
      {code:'MN62', name:'Darial Pass', lat:42.686498, lon:44.626543},
      {code:'MP04', name:'Lesnoe', lat:43.792241, lon:43.827566},
      {code:'MP23', name:'Mayskiy', lat:43.620669, lon:44.092834},
      {code:'MP61', name:'Malgobek', lat:43.512859, lon:44.586159},
      {code:'MP74', name:'Mozdok', lat:43.751921, lon:44.623475},
    ],
    185: [
      // Syria — 19 objectives (11 suppressed: match base names, shown as bases only)
      // Suppressed: YB01:Ramat David, BU99:Hama, BR38:King Hussein Air College,
      // CV25:Abu al-Duhur, YC34:Beirut-Rafic Hariri, CT05:An Nasiriyah, CU72:Tiyas,
      // BA52:Hatay, BU23:Rene Mouawad, CA24:Minakh, CA70:Kuweires
      {code:'BU71', name:'Al Qusayr',     lat:34.450667, lon:36.560651},
      {code:'CT38', name:'Sadad',          lat:34.225287, lon:37.229534},
      {code:'BV87', name:'Idlib',          lat:35.876085, lon:36.639704},
      {code:'BU95', name:'Homs',           lat:34.781612, lon:36.726727},
      {code:'CU55', name:'Al-Mukharam',    lat:34.853112, lon:37.367469},
      {code:'YA46', name:'Dayr Allah',     lat:32.208904, lon:35.590265},
      {code:'YD68', name:'Marqueh',        lat:35.041526, lon:35.944426},
      {code:'BV82', name:'Kafr Zita',      lat:35.475981, lon:36.602508},
      {code:'CV31', name:'Hamra',          lat:35.330627, lon:37.207996},
      {code:'YB53', name:'Tiberias',       lat:32.816660, lon:35.721553},
      {code:'YB07', name:'Tyre',           lat:33.204926, lon:35.225158},
      {code:'YB47', name:'Kiryat Shmona',  lat:33.211874, lon:35.644171},
      {code:'BV35', name:'Sheekhaneh',     lat:35.727867, lon:36.080346},
      {code:'BS45', name:'Nawa',           lat:32.986856, lon:36.242722},
      {code:'YC48', name:'Wujah Al-Hajar', lat:34.191314, lon:35.695427},
      {code:'BT22', name:'Madaya',         lat:33.626135, lon:36.055685},
      {code:'CA00', name:'Sarmada',        lat:36.201161, lon:36.777574},
      {code:'BA30', name:'Samandag',       lat:36.108275, lon:36.011832},
      {code:'BT37', name:'Baalbek',        lat:34.064131, lon:36.178297},
    ],
  },
};
const SCORE_EXCLUDE_KEYS = new Set([
  'airbase_Ramstein',         // Germany — excluded from objective counter
  'airbase_Laage',            // Germany — excluded from objective counter
  'airbase_Vaziani',          // Caucasus — excluded from objective counter
  'airbase_Anapa-Vityazevo',  // Caucasus — excluded from objective counter
  'airbase_Jiroft',           // Persian Gulf — excluded from objective counter
  'airbase_Liwa AFB',         // Persian Gulf — excluded from objective counter
  'airbase_Gaziantep',        // Syria — excluded from objective counter
  'airbase_Ben Gurion',       // Syria — excluded from objective counter
]);
const MAP_CENTRES = {
  189: {lat:26.057, lon:55.239, zoom:8},  // Persian Gulf
  190: {lat:43.2,   lon:42.0,  zoom:8},  // Caucasus
  192: {lat:51.762, lon:10.430, zoom:8},  // Germany
  193: {lat:43.2,   lon:42.0,  zoom:8},  // Caucasus Inverted
  185: {lat:34.639, lon:36.466, zoom:8},  // Syria
};

// ════════════════════════════════════════════════════════════════════
//  SVG AIRCRAFT ICONS — Tacview plan-view silhouettes, 32×32 viewBox
//  All nose-up (north). Rotated at runtime by heading.
//  Ground vehicles: NOT aircraft-style — all use diamond.
// ════════════════════════════════════════════════════════════════════
// ════════════════════════════════════════════════════════════════════
//  AIRCRAFT ICONS  —  Tacview-style top-down silhouettes
//  ViewBox 0 0 32 32.  Nose points UP (north).  Rotated by heading at runtime.
//  Each shape traces the plan-view projection of the Tacview 3D mesh:
//  fuselage spine + wing panels + tail surfaces + engine pods where visible.
//  Rotor-craft: semi-transparent rotor disc circle + blade ellipses + body.
// ════════════════════════════════════════════════════════════════════
const AC_ICONS = {
  // All icons in 64×64 viewBox

  // ── modernFW: Mirage 2000 (tailless delta) ────────────────────────
  'modernFW': `
    <path d="M32,4 L34.5,20 L40,48 L36,56 L32,60 L28,56 L24,48 L29.5,20 Z"/>
    <path d="M29.5,20 L4,54 L24,48 Z"/>
    <path d="M34.5,20 L60,54 L40,48 Z"/>`,

  // ── legacyFW: AV-8B Harrier ───────────────────────────────────────
  'legacyFW': `
    <path d="M32,4 L35,16 L36,38 L34,46 L32,50 L30,46 L28,38 L29,16 Z"/>
    <path d="M29,16 L8,36 L24,33 L28,38 Z"/>
    <path d="M35,16 L56,36 L40,33 L36,38 Z"/>
    <path d="M28,38 L14,54 L25,50 L28,44 Z"/>
    <path d="M36,38 L50,54 L39,50 L36,44 Z"/>
    <line x1="18" y1="38" x2="16" y2="44" stroke-width="3"/>
    <line x1="46" y1="38" x2="48" y2="44" stroke-width="3"/>`,

  // ── prop: P-51D Mustang ───────────────────────────────────────────
  'prop': `
    <ellipse cx="32" cy="34" rx="4" ry="26"/>
    <circle cx="32" cy="9" r="5" fill="currentColor" opacity=".22"/>
    <line x1="20" y1="9" x2="44" y2="9" stroke-width="3.5" stroke-linecap="round"/>
    <path d="M28,22 L7,33 L7,38 L28,36 Z"/>
    <path d="M36,22 L57,33 L57,38 L36,36 Z"/>
    <path d="M29,50 L24,57 L30,55 Z"/>
    <path d="M35,50 L40,57 L34,55 Z"/>
    <rect x="29.5" y="51" width="5" height="3.5" rx="1.5"/>
    <path d="M28,52 L22,55 L28,54 Z"/>
    <path d="M36,52 L42,55 L36,54 Z"/>
    <rect x="30" y="37" width="4" height="8" rx="1.5"/>`,

  // ── transport: C-130J Hercules ────────────────────────────────────
  'transport': `
    <rect x="26" y="6" width="12" height="52" rx="6"/>
    <rect x="2" y="19" width="60" height="9" rx="0"/>
    <circle cx="12" cy="19" r="5.5" opacity=".75"/>
    <circle cx="22" cy="19" r="5.5" opacity=".75"/>
    <circle cx="42" cy="19" r="5.5" opacity=".75"/>
    <circle cx="52" cy="19" r="5.5" opacity=".75"/>
    <rect x="29.5" y="53" width="5" height="9" rx="2"/>
    <rect x="12" y="52" width="40" height="5" rx="2.5"/>`,

  // ── awacs: C-130 body + solid radar dome ──────────────────────────
'awacs': `
    <rect x="26" y="6" width="12" height="52" rx="6"/>
    <rect x="2" y="25" width="60" height="9" rx="0"/>
    <circle cx="12" cy="25" r="5.5" opacity=".75"/>
    <circle cx="22" cy="25" r="5.5" opacity=".75"/>
    <circle cx="42" cy="25" r="5.5" opacity=".75"/>
    <circle cx="52" cy="25" r="5.5" opacity=".75"/>
    <rect x="29.5" y="53" width="5" height="9" rx="2"/>
    <rect x="12" y="52" width="40" height="5" rx="2.5"/>
    <circle cx="32" cy="30" r="13" fill="currentColor" opacity=".9"/>`,

  // ── attackRW: SA-342 Gazelle ──────────────────────────────────────
  'attackRW': `
    <circle cx="32" cy="22" r="22" fill="currentColor" opacity=".5"/>
    <ellipse cx="32" cy="22" rx="22" ry="2" transform="rotate(45,32,22)"/>
    <ellipse cx="32" cy="22" rx="22" ry="2" transform="rotate(135,32,22)"/>
    <rect x="28" y="10" width="8" height="34" rx="4"/>
    <line x1="28" y1="28" x2="12" y2="28" stroke-width="4" stroke-linecap="round"/>
    <line x1="36" y1="28" x2="52" y2="28" stroke-width="4" stroke-linecap="round"/>
    <ellipse cx="19" cy="28" rx="2" ry="4"/>
    <ellipse cx="45" cy="28" rx="2" ry="4"/>
    <rect x="30.5" y="42" width="3" height="14" rx="1.5"/>
    <line x1="24" y1="54" x2="40" y2="54" stroke-width="3.5" stroke-linecap="round"/>`,

  // ── CH47: CH-47 Chinook ───────────────────────────────────────────
  'CH47': `
    <circle cx="32" cy="18" r="16" fill="currentColor" opacity=".15"/>
    <circle cx="32" cy="18" r="16" fill="none" stroke="currentColor" stroke-width="2"/>
    <circle cx="32" cy="46" r="17" fill="currentColor" opacity=".15"/>
    <circle cx="32" cy="46" r="17" fill="none" stroke="currentColor" stroke-width="2"/>
    <rect x="25" y="10" width="14" height="42" rx="7"/>`,

  // ── Mi8: Mi-8/17 Hip ──────────────────────────────────────────────
  'Mi8': `
    <circle cx="32" cy="24" r="22" fill="currentColor" opacity=".5"/>
    <ellipse cx="32" cy="24" rx="22" ry="3"/>
    <ellipse cx="32" cy="24" rx="22" ry="3" transform="rotate(60,32,24)"/>
    <ellipse cx="32" cy="24" rx="22" ry="3" transform="rotate(120,32,24)"/>
    <rect x="25" y="10" width="14" height="32" rx="7"/>
    <rect x="30.5" y="40" width="3" height="18" rx="1.5"/>
    <line x1="24" y1="56" x2="40" y2="56" stroke-width="4" stroke-linecap="round"/>`,

  // ── huey: UH-1H Iroquois ──────────────────────────────────────────
  'huey': `
    <circle cx="32" cy="24" r="24" fill="currentColor" opacity=".5"/>
    <ellipse cx="32" cy="24" rx="24" ry="1.5" transform="rotate(45,32,24)"/>
    <ellipse cx="32" cy="24" rx="24" ry="1.5" transform="rotate(135,32,24)"/>
    <rect x="27" y="14" width="10" height="24" rx="5"/>
    <rect x="30.5" y="36" width="3" height="18" rx="1.5"/>
    <line x1="25" y1="52" x2="39" y2="52" stroke-width="3" stroke-linecap="round"/>`,

  // ── f15: F-15C/E Strike Eagle ─────────────────────────────────────
  'f15': `
  <path d="M 31.8148,0.0 L 31.6215,0.2532 L 30.8275,2.2385 L 30.212,5.137 L 29.9937,8.5119 L 29.8944,18.5176 L 27.2143,18.5376 L 27.1547,22.7859 L 26.1025,25.1484 L 25.5269,27.5704 L 25.4077,31.4815 L 11.0542,46.0135 L 11.0344,46.7481 L 13.3571,51.2149 L 18.6975,49.865 L 25.2489,49.865 L 25.2489,52.0289 L 25.4871,53.4781 L 23.1048,56.3369 L 23.1445,54.848 L 17.8637,60.8831 L 17.824,61.7368 L 19.4519,64.0 L 26.4003,62.5309 L 27.7801,59.4935 L 27.9885,57.6869 L 28.4749,59.6721 L 30.8672,59.6721 L 31.3238,57.538 L 31.6017,57.528 L 31.6314,59.5927 L 31.9714,59.6097 L 31.9999,59.611 L 32.0286,59.6097 L 32.3686,59.5927 L 32.3983,57.528 L 32.6762,57.538 L 33.1328,59.6721 L 35.5251,59.6721 L 36.0115,57.6869 L 36.2199,59.4935 L 37.5997,62.5309 L 44.5481,64.0 L 46.176,61.7368 L 46.1363,60.8831 L 40.8555,54.848 L 40.8952,56.3369 L 38.5129,53.4781 L 38.7511,52.0289 L 38.7511,49.865 L 45.3025,49.865 L 50.6429,51.2149 L 52.9656,46.7481 L 52.9458,46.0135 L 38.5923,31.4815 L 38.4731,27.5704 L 37.8975,25.1484 L 36.8453,22.7859 L 36.7857,18.5376 L 34.1056,18.5176 L 34.0063,8.5119 L 33.788,5.137 L 33.1725,2.2385 L 32.3785,0.2532 L 32.1852,0.0 Z"/>`,

  // ── su33: Su-33 Flanker-D ─────────────────────────────────────────
  'su33': `
  <path d="M 31.8424,0.0 C 30.6634,2.5058 30.203,5.3095 29.8728,8.0391 C 29.7873,10.0297 29.9837,12.0721 29.7212,14.0301 C 28.9507,16.0064 29.1638,18.2502 28.5347,20.2516 C 27.218,23.265 24.9374,25.6744 23.057,28.3346 C 22.5,28.7078 22.151,30.9075 23.1517,30.1774 C 24.2932,29.7066 25.4346,29.2358 26.576,28.7651 C 26.7047,29.9086 26.3977,31.1002 25.3703,31.742 C 20.6504,36.1126 15.9305,40.4832 11.2106,44.8537 C 11.2256,42.8577 11.2407,40.8617 11.2557,38.8657 C 10.7123,37.5049 9.6969,38.8221 9.9921,39.7539 C 9.999,43.269 10.006,46.7842 10.0129,50.2993 C 11.1313,50.1844 11.2955,50.9786 12.4647,50.316 C 16.8446,49.0451 21.2245,47.7741 25.6044,46.5032 C 25.6979,47.4899 25.6737,48.4299 24.7519,49.0143 C 22.43,51.4839 20.108,53.9534 17.7861,56.423 C 18.3736,57.2892 18.9611,58.1554 19.5486,59.0216 C 21.6802,58.7429 23.8118,58.4642 25.9434,58.1855 C 26.2944,57.8182 26.9527,55.5155 27.0785,56.5675 C 27.2367,57.3014 27.2748,58.8051 28.3281,58.5696 C 29.3581,58.6902 30.2957,58.6665 30.4626,57.4398 C 30.5574,59.1307 30.4281,60.8938 30.6634,62.5395 C 31.1778,63.0037 31.5115,64.5587 32.3355,64.0 C 32.882,63.1641 33.6845,62.4105 33.4474,61.3224 C 33.4768,60.0282 33.5062,58.734 33.5356,57.4398 C 33.7086,58.7071 34.7225,58.6618 35.7665,58.5696 C 36.778,58.7039 36.7661,57.1795 36.9376,56.4548 C 37.1096,55.7693 37.7101,57.7827 38.0548,58.1855 C 40.1864,58.4642 42.318,58.7429 44.4496,59.0216 C 45.0371,58.1554 45.6247,57.2892 46.2122,56.423 C 43.6061,53.6512 40.9999,50.8794 38.3938,48.1076 C 38.2627,46.9834 38.2966,46.0789 39.589,46.85 C 44.0187,48.1354 48.4484,49.4208 52.8781,50.7062 C 53.3378,50.0825 54.4682,50.366 53.9881,48.8993 C 53.9947,45.5397 54.0013,42.1801 54.0079,38.8205 C 53.4229,37.5277 52.4431,38.8932 52.7495,39.799 C 52.7622,41.4839 52.7749,43.1688 52.7876,44.8537 C 47.8014,40.2365 42.8151,35.6193 37.8289,31.0021 C 37.4951,30.498 36.9859,28.5278 37.8536,28.943 C 39.043,29.4336 40.2323,29.9241 41.4217,30.4146 C 41.5568,29.4072 41.3106,28.5301 40.5597,27.8253 C 38.7868,25.3438 36.6792,23.072 35.4595,20.2438 C 34.8109,18.1432 35.0606,15.7878 34.1683,13.7386 C 34.1055,10.4785 34.3648,7.1689 33.443,3.9957 C 33.1449,2.6284 32.8184,1.2423 32.1558,0.0 C 32.0513,0.0077 31.9469,0.0036 31.8424,0.0 Z"/>`,

  // ── su27: Su-27 Flanker / J-11 ────────────────────────────────────
  'su27': `
  <path d="M 31.9968,0.0 C 30.7733,1.3503 30.6264,3.3042 30.2378,5.0091 C 30.1418,10.0054 29.2555,14.9404 28.4958,19.8663 C 27.8439,22.9203 26.9734,25.9126 25.9446,28.8602 C 26.1348,29.8945 25.84,30.7132 24.9112,31.2499 C 20.1818,35.5164 15.4524,39.7828 10.723,44.0493 C 10.7338,42.5811 10.7446,41.113 10.7555,39.6448 C 9.8542,39.709 10.5507,41.376 10.3265,42.1192 C 10.3183,44.6841 10.3101,47.2491 10.302,49.814 C 15.2707,48.4922 20.2394,47.1704 25.208,45.8485 C 25.0617,46.7091 25.6792,47.8727 24.9686,48.5095 C 22.4912,50.943 20.0138,53.3766 17.5364,55.8102 C 18.0555,56.6422 18.5746,57.4743 19.0936,58.3063 C 21.2157,58.1231 23.3378,57.9399 25.4599,57.7567 C 25.8111,56.7949 26.1622,55.8331 26.5134,54.8713 C 26.5973,55.8331 26.6813,56.7949 26.7653,57.7567 C 27.7958,57.7644 28.8263,57.7721 29.8568,57.7797 C 29.9738,57.3106 30.1358,54.8691 30.2189,55.883 C 30.4035,57.9427 30.5882,60.0024 30.7728,62.0621 C 31.6177,62.2758 31.4138,63.6967 32.0106,64.0 C 32.4777,63.3852 32.7241,62.2768 33.2548,61.754 C 33.444,59.643 33.6333,57.5319 33.8226,55.4209 C 34.1551,56.1241 33.6287,57.8183 34.6071,57.7763 C 35.421,57.5902 36.9098,58.135 37.2616,57.4486 C 37.3934,56.8486 37.3306,54.7766 37.5927,55.1618 C 37.9935,55.9872 38.1248,57.1647 38.6942,57.77 C 40.7649,57.9488 42.8356,58.1276 44.9064,58.3063 C 45.4254,57.4743 45.9445,56.6422 46.4636,55.8102 C 43.8758,53.2682 41.288,50.7263 38.7003,48.1843 C 38.9622,47.5565 38.2831,45.6535 39.2403,45.9678 C 44.0595,47.2499 48.8788,48.5319 53.698,49.814 C 53.6872,46.4243 53.6764,43.0345 53.6655,39.6448 C 52.7652,39.7091 53.4792,41.3759 53.2627,42.1192 C 53.1897,42.8937 53.6262,44.8028 52.5879,43.4278 C 47.7438,39.0577 42.8996,34.6876 38.0554,30.3176 C 38.2464,28.2549 37.1065,26.4039 36.6165,24.4495 C 35.6975,21.1417 35.0944,17.7678 34.6564,14.3649 C 34.178,11.16 33.7996,7.9434 33.7481,4.7002 C 33.2601,3.1188 33.209,1.2326 31.9968,0.0 Z"/>`,

  // ── mig29: MiG-29 Fulcrum ─────────────────────────────────────────
  'mig29': `
  <path d="M 31.6189,0.0 L 31.3869,0.4058 L 30.7326,1.9878 L 30.3931,3.4125 L 30.0527,11.6639 L 27.9208,18.4578 L 26.6322,23.19 L 25.4375,28.3909 L 25.4141,30.2181 L 10.4441,43.9932 L 9.6944,44.9771 L 9.3665,45.9377 L 9.4602,49.9672 L 24.8284,47.3198 L 24.5238,51.2791 L 16.6757,60.603 L 16.6289,61.5869 L 17.4254,64.0 L 24.6293,60.4859 L 26.2925,56.9251 L 26.6088,58.2838 L 30.0995,58.3658 L 30.3103,56.3394 L 31.1068,55.8005 L 31.997,56.2311 L 31.9999,56.2324 L 32.0029,56.2311 L 32.8932,55.8005 L 33.6897,56.3394 L 33.9005,58.3658 L 37.3912,58.2838 L 37.7074,56.9251 L 39.3707,60.4859 L 46.5745,64.0 L 47.3711,61.5869 L 47.3241,60.603 L 39.4761,51.2791 L 39.1716,47.3198 L 54.5397,49.9672 L 54.6335,45.9377 L 54.3054,44.9771 L 53.5558,43.9932 L 38.5859,30.2181 L 38.5624,28.3909 L 37.3676,23.19 L 36.0792,18.4578 L 33.9473,11.6639 L 33.6068,3.4125 L 33.2672,1.9878 L 32.6129,0.4058 L 32.381,0.0 L 31.9999,0.0147 Z"/>`,

  // ── m2000: Mirage 2000 ────────────────────────────────────────────
  'm2000': `
  <path d="M 31.999,0.0 L 31.999,0.0079 L 30.8453,4.436 L 30.1085,8.8366 L 29.8497,11.9229 L 29.8098,16.8412 L 28.6948,21.2617 L 27.5996,21.4409 L 27.5399,22.8148 L 27.0222,23.452 L 26.8031,24.1688 L 26.7832,26.4587 L 12.3385,49.6808 L 11.8317,50.6945 L 11.6064,52.1025 L 11.6626,53.7357 L 27.9953,54.8059 L 28.0516,58.6919 L 29.009,58.6356 L 29.5722,63.8733 L 31.9729,64.0 L 31.9729,63.9858 L 32.0272,63.9858 L 32.0272,64.0 L 34.4278,63.8733 L 34.991,58.6356 L 35.9484,58.6919 L 36.0047,54.8059 L 52.3374,53.7357 L 52.3936,52.1025 L 52.1685,50.6945 L 51.6615,49.6808 L 37.2168,26.4587 L 37.1969,24.1688 L 36.9778,23.452 L 36.4601,22.8148 L 36.4004,21.4409 L 35.3052,21.2617 L 34.1902,16.8412 L 34.1503,11.9229 L 33.8915,8.8366 L 33.1547,4.436 L 32.001,0.0079 L 32.001,0.0 L 31.9999,0.004 Z"/>`,

  // ── jf17: JF-17 Thunder ───────────────────────────────────────────
  'jf17': `
  <path d="M 32.1174,0.0 C 29.9751,5.2011 29.9508,10.9306 29.7643,16.4655 C 29.7034,18.1996 29.8319,19.9563 29.3061,21.635 C 28.1115,21.4494 27.9253,22.8084 27.3859,23.5769 C 26.1754,26.2083 25.4823,29.109 25.2553,31.9933 C 25.0868,33.0242 25.6271,34.3687 24.5334,34.9902 C 20.8412,38.527 17.1491,42.0639 13.457,45.6008 C 12.6603,45.5291 13.3029,43.8954 13.0883,43.192 C 12.9758,42.1178 13.2968,40.9052 12.8979,39.9224 C 12.2809,39.2324 12.7126,38.2077 12.2504,37.4019 C 11.6017,39.2618 12.0569,41.2836 11.9214,43.2188 C 11.8677,44.4968 12.0273,45.8328 11.8442,47.0755 C 11.3621,47.5956 11.0146,49.1084 11.6774,49.3107 C 12.5625,49.4374 13.3326,49.7063 14.3518,49.577 C 18.4902,49.5776 22.6287,49.5781 26.7671,49.5787 C 26.6828,50.6697 26.9049,51.8897 26.6395,52.9045 C 24.2519,55.2666 21.8643,57.6287 19.4767,59.9909 C 19.8332,60.7134 19.5136,62.1064 20.4044,62.3366 C 22.9519,62.3302 25.4993,62.3239 28.0468,62.3176 C 28.5939,61.8515 29.1993,60.2565 29.749,60.5495 C 29.9714,62.7365 30.0826,63.8299 30.0826,63.8299 C 31.4395,63.8299 32.7965,63.8299 34.1534,63.8299 C 34.2697,62.686 34.386,61.542 34.5024,60.398 C 35.3019,60.6198 35.5817,61.9803 36.3416,62.318 C 38.889,62.3243 41.4364,62.3306 43.9838,62.337 C 44.5778,61.8334 44.6548,60.576 44.6512,59.8838 C 42.2636,57.5217 39.876,55.1595 37.4884,52.7974 C 37.4819,51.7245 37.4754,50.6516 37.4689,49.5787 C 42.2164,49.5781 46.9638,49.5774 51.7113,49.5768 C 52.6016,49.3174 53.1642,49.1362 52.8631,47.8767 C 51.9031,46.7625 52.4607,45.235 52.3146,43.8991 C 52.2304,41.9591 52.4854,39.9693 52.1834,38.0613 C 51.9375,36.5813 51.5744,38.8707 51.6839,39.4124 C 50.7568,40.3906 51.3041,41.8398 51.1484,43.0644 C 50.9636,43.8251 51.5126,45.3823 50.8319,45.6049 C 46.8731,41.9212 42.9774,38.0962 39.0429,34.3582 C 39.1252,30.7463 38.3869,27.1272 36.9771,23.8084 C 36.3767,23.0537 36.2543,21.5365 35.0519,21.6503 C 34.5495,20.7781 34.5158,19.4451 34.5129,18.3579 C 34.349,12.7702 34.4203,7.0501 32.7392,1.6616 C 32.5323,1.1088 32.3226,0.5483 32.1174,0.0 Z"/>`,

  // ── f16: F-16 Fighting Falcon ─────────────────────────────────────
  'f16': `
  <path d="M 31.9752,0.8459 C 31.9876,2.6707 31.9714,0.313 31.976,2.0078 C 31.9772,1.9861 32.0403,0.0 31.651,1.8609 C 31.0007,4.018 30.0217,6.2204 29.9603,8.5516 C 29.5878,11.2502 29.4702,13.9992 28.9345,16.6652 C 27.9219,20.4238 26.5612,24.133 26.1248,28.0133 C 26.0681,28.9376 26.2229,29.9726 25.1862,30.3839 C 21.0002,33.7114 16.8142,37.0388 12.6282,40.3662 C 12.6282,39.0649 12.6282,37.7638 12.6282,36.4625 C 13.3461,36.7325 12.3374,34.367 11.7413,35.3598 C 11.0508,36.3772 11.7908,36.485 11.6246,37.5605 C 11.5874,39.8971 11.55,42.2336 11.5128,44.5701 C 10.8516,44.6571 10.8123,46.801 11.8806,46.2861 C 13.2992,46.812 12.8432,45.4599 13.7889,45.516 C 18.1637,45.5296 22.5384,45.5432 26.9133,45.5568 C 26.899,47.2156 26.8846,48.8744 26.8704,50.533 C 24.7255,52.5493 22.5806,54.5656 20.4356,56.5817 C 20.5154,57.7247 20.3386,58.9574 20.5711,60.0468 C 20.9858,61.1015 22.1675,60.574 23.039,60.6865 C 24.4449,60.6766 25.8507,60.6669 27.2565,60.6571 C 26.7449,59.2193 28.7581,60.2755 28.85,59.4548 C 28.6861,58.8201 29.0187,56.7822 29.4226,58.1061 C 29.4727,59.1708 29.5229,60.2358 29.573,61.3007 C 30.3003,61.4815 31.9265,60.7636 31.544,62.0544 C 31.5839,62.7168 31.213,64.0 32.3148,63.5953 C 32.8418,63.1855 32.1536,61.6899 32.6409,61.2897 C 33.5725,61.2908 34.7984,61.6001 34.4272,60.2355 C 34.5747,59.4404 34.3095,58.1751 34.6994,57.656 C 35.6733,57.663 34.5312,59.6769 35.4081,59.7622 C 36.822,59.2753 36.3413,60.7239 37.2973,60.6505 C 39.1554,60.6635 41.0134,60.6763 42.8715,60.6893 C 43.9026,59.8145 43.3425,58.382 43.507,57.2035 C 43.7085,56.1585 42.3913,55.7588 41.8673,55.0221 C 40.2715,53.5222 38.6759,52.0222 37.0803,50.5224 C 37.0659,48.8636 37.0515,47.2048 37.0373,45.546 C 41.6132,45.5318 46.1891,45.5174 50.7649,45.5031 C 50.374,46.8049 51.9872,46.1023 52.7249,46.2753 C 53.1462,45.4413 52.5597,44.6583 52.4284,43.9564 C 52.3887,41.469 52.349,38.9817 52.3092,36.4944 C 53.1877,36.3798 51.5145,34.0707 51.2756,35.7677 C 50.7724,36.5788 51.6329,36.8018 51.3225,37.9593 C 51.149,38.5493 51.7072,40.6554 50.9685,40.0738 C 46.6251,36.6214 42.2817,33.169 37.9383,29.7165 C 37.836,25.3384 36.2394,21.1952 35.1177,17.008 C 34.4725,14.4585 34.4514,11.7847 34.0638,9.184 C 33.9341,7.3551 33.632,5.5637 32.9467,3.8548 C 32.623,2.8518 32.2992,1.8489 31.9754,0.8459 Z"/>`,

  // ── f14: F-14 Tomcat ──────────────────────────────────────────────
  'f14': `
  <path d="M 32.2487,2.413 L 32.2487,2.4251 L 31.8648,2.4678 L 30.5485,5.8679 L 29.6711,11.2974 L 29.5066,14.8622 L 29.342,21.3333 L 26.6549,21.3333 L 26.6001,22.5946 L 13.1638,56.048 L 13.4929,58.0223 L 14.4253,59.5579 L 15.7414,61.3129 L 17.8802,63.4515 L 25.0645,61.6965 L 25.5031,60.49 L 26.3257,60.49 L 26.3808,63.0676 L 27.0936,63.0676 L 27.9712,60.5451 L 30.9324,60.49 L 31.097,62.6837 L 32.2487,62.734 L 32.2487,62.7387 L 32.3035,62.7364 L 32.3585,62.7387 L 32.3585,62.734 L 33.51,62.6837 L 33.6745,60.49 L 36.636,60.5451 L 37.5134,63.0676 L 38.2264,63.0676 L 38.2812,60.49 L 39.1038,60.49 L 39.5427,61.6965 L 46.7269,63.4515 L 48.8656,61.3129 L 50.1819,59.5579 L 51.1143,58.0223 L 51.4431,56.048 L 38.0071,22.5946 L 37.9523,21.3333 L 35.2649,21.3333 L 35.1004,14.8622 L 34.9358,11.2974 L 34.0584,5.8679 L 32.7421,2.4678 L 32.3585,2.4253 L 32.3585,2.413 L 32.3035,2.419 Z"/>`,

  // ── f18: F/A-18C Hornet ───────────────────────────────────────────
  'f18': `
  <path d="M 30.2313,3.8389 l 1.042,2.0291 l 0.5484,2.5227 l 0.2742,7.1294 l 0.7678,1.5904 l 0.329,3.126 l 0.5484,4.3325 l 0.8226,3.455 l 0.5484,2.4679 l 0.1097,2.9066 l 14.3136,6.6907 l -0.0548,-2.9066 l 0.329,-0.329 l 0.1645,-0.9323 l 0.329,0 l 0,9.3231 l -0.2194,-0.0548 l 0,0.4387 l -15.1362,0.9323 l 1.4807,3.7292 l 0.0548,1.9195 l 4.7164,5.539 l 0.0548,2.5227 l -0.2742,0.5484 l -1.0968,0.2742 l -6.91,-3.2905 l -0.2742,1.2065 l -1.6452,-0.0548 l -0.7129,-2.084 Z"/>
  <path d="M 30.2374,3.8356 l -1.042,2.0291 l -0.5484,2.5227 l -0.2742,7.1294 l -0.7678,1.5904 l -0.329,3.126 l -0.5484,4.3325 l -0.8226,3.455 l -0.5484,2.4679 l -0.1097,2.9066 l -14.3136,6.6907 l 0.0548,-2.9066 l -0.329,-0.329 l -0.1645,-0.9323 l -0.329,0 l 0,9.3231 l 0.2194,-0.0548 l 0,0.4387 l 15.1362,0.9323 l -1.4807,3.7292 l -0.0548,1.9195 l -4.7164,5.539 l -0.0548,2.5227 l 0.2742,0.5484 l 1.0968,0.2742 l 6.91,-3.2905 l 0.2742,1.2065 l 1.6452,-0.0548 l 0.7129,-2.084 Z"/>
  <rect x="29.9571" y="5.3196" width="1.1517" height="51.8252"/>`,

  // ── default-air fallback (modernFW shape) ─────────────────────────
  'default-air': `
    <path d="M32,4 L34.5,20 L40,48 L36,56 L32,60 L28,56 L24,48 L29.5,20 Z"/>
    <path d="M29.5,20 L4,54 L24,48 Z"/>
    <path d="M34.5,20 L60,54 L40,48 Z"/>`,
};

// DCS name → icon key
// Order matters — specific before generic. All lowercased.
function iconKey(name) {
  if (!name) return 'modernFW';
  const n = name.toLowerCase();

  // transport
  if (n.includes('an-30') || n.includes('an30'))    return 'transport';
  if (n.includes('kc-30') || n.includes('kc30'))    return 'transport';
  if (n.includes('c-130') || n.includes('c130'))    return 'transport';
  if (n.includes('il-76') || n.includes('il76'))    return 'transport';
  if (n.includes('kc-135') || n.includes('kc135') || n.includes('kc135stratotanker')) return 'transport';

  // awacs — E2-D / E2 A xxx (no hyphen between E and 2 in DCS)
  if (n.startsWith('e2') || n.includes('e-2c') || n.includes('e-2d')) return 'awacs';

  // attackRW
  if (n.includes('ka-50') || n.includes('ka50'))    return 'attackRW';
  if (n.includes('ah-64') || n.includes('ah64'))    return 'attackRW';
  if (n.includes('mi-24') || n.includes('mi24'))    return 'attackRW';
  if (n.includes('sa342') || n.includes('sa-342'))  return 'attackRW';
  if (n.includes('oh58d') || n.includes('oh-58'))   return 'attackRW';

  // CH47
  if (n.includes('ch-47') || n.includes('ch47'))    return 'CH47';

  // Mi8 — check before any generic mi- catch
  if (n.includes('mi-8')  || n.includes('mi8'))     return 'Mi8';

  // huey
  if (n.includes('uh-1')  || n.includes('uh1'))     return 'huey';

  // prop
  if (n.includes('tf-51') || n.includes('tf51'))    return 'prop';
  if (n.includes('p-51')  || n.includes('p51'))     return 'prop';

  // legacyFW — su-25 before su-27; mig-15/19/21 before mig-29
  if (n.includes('su-25') || n.includes('su25'))    return 'legacyFW';
  if (n.includes('mig-21')|| n.includes('mig21'))   return 'legacyFW';
  if (n.includes('mig-15')|| n.includes('mig15'))   return 'legacyFW';
  if (n.includes('mig-19')|| n.includes('mig19'))   return 'legacyFW';
  if (n.includes('f-4e')  || n === 'f-4')           return 'legacyFW';
  if (n.includes('f-5e')  || n.includes('f-5e-3'))  return 'legacyFW';
  if (n.includes('miragef1') || n.includes('mirage f1')) return 'legacyFW';
  if (n.includes('ajs37') || n.includes('ajs-37'))  return 'legacyFW';
  if (n.includes('c-101') || n.includes('c101'))    return 'legacyFW';
  if (n.includes('l-39')  || n.includes('l39'))     return 'legacyFW';
  if (n.includes('mb-339')|| n.includes('mb339'))   return 'legacyFW';
  if (n.includes('f-86')  || n.includes('f86'))     return 'legacyFW';
  if (n.includes('av8b')  || n.includes('av-8'))    return 'legacyFW';
  if (n.includes('a-10c') || n.includes('a-10'))    return 'legacyFW';
  if (n.includes('su-25t'))                         return 'legacyFW';

  // modernFW — f-15 before any f-5 risk (already caught above anyway)
  if (n.includes('f-15')  || n.includes('f15'))     return 'f15';
  if (n.includes('f-16')  || n.includes('f16'))     return 'f16';
  if (n.includes('fa-18') || n.includes('fa18')
   || n.includes('f/a-18')|| n.includes('hornet'))  return 'f18';
  if (n.includes('jf-17') || n.includes('jf17'))    return 'jf17';
  if (n.includes('su-27') || n.includes('su27'))    return 'su27';
  if (n.includes('su-33') || n.includes('su33'))    return 'su33';
  if (n.includes('j-11')  || n.includes('j11'))     return 'su27';
  if (n.includes('mig-29')|| n.includes('mig29'))   return 'mig29';
  if (n.includes('m-2000')|| n.includes('m2000')
   || n.includes('mirage'))                          return 'm2000';
  if (n.includes('f-14')  || n.includes('f14')
   || n.includes('tomcat'))                          return 'f14';

  return 'modernFW';
}

function makeGroundDiamond(color, sz) {
  const h = sz / 2;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${sz}" height="${sz}" viewBox="0 0 ${sz} ${sz}" style="filter:drop-shadow(0 0 1px #000) drop-shadow(0 1px 1px #000)">
    <polygon points="${h},2 ${sz-2},${h} ${h},${sz-2} 2,${h}"
      fill="${color}" stroke="${color}" stroke-width=".5" opacity=".85"/>
  </svg>`;
}


function makeACSVG(key, color, sz, hdg, selected, isHuman) {
  const body = AC_ICONS[key] || AC_ICONS['default-air'];
  const rot = hdg != null ? `rotate(${hdg},32,32)` : '';
  const sel = selected
    ? `<circle cx="32" cy="32" r="28" fill="none" stroke="#fff" stroke-width="2" opacity=".55"/>`
    : '';
  // Both player and AI icons get black outline; player outline is thicker
  const outlineW = isHuman ? '4' : '2.5';
  const outline = `<g transform="${rot}" style="color:#000" fill="#000" stroke="#000" stroke-width="${outlineW}" stroke-linejoin="round" stroke-linecap="round" opacity=".85">${body}</g>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${sz}" height="${sz}" viewBox="0 0 64 64"
    style="color:${color}">${outline}
    <g transform="${rot}" fill="${color}" stroke="${color}" stroke-width=".7" opacity=".93">${body}</g>${sel}</svg>`;
}

function leafletIcon(cat, name, coalition, hdg, sel, isHuman, forceGnd) {
  const blue = coalition === 'Friendlies';
  const color = blue ? '#58a6ff' : '#f85149';


  // forceGnd=true for SAM units that are ai_air category but render as ground diamonds
  if (cat === 'ground' || forceGnd) {
    const sz = Math.round(14 * UI_SCALE);
    const html = makeGroundDiamond(color, sz);
    return L.divIcon({ html, className:'', iconSize:[sz,sz], iconAnchor:[sz/2,sz/2] });
  }

  const key = iconKey(name);
  const sz = Math.round((isHuman ? 36 : 28) * UI_SCALE);
  const svg = makeACSVG(key, color, sz, hdg, sel, isHuman);
  return L.divIcon({ html:svg, className:'', iconSize:[sz,sz], iconAnchor:[sz/2,sz/2] });
}


function trackIdxAt(track, t, hint){
  let lo=0, hi=track.length-1;
  // Fast path: hint is still valid or one step ahead
  if(hint>=0 && hint<track.length){
    if(track[hint].t<=t && (hint===hi||track[hint+1].t>t)) return hint;
    if(hint<hi && track[hint+1].t<=t){
      // Try scanning forward a few steps before full binary search
      for(let i=hint+1;i<=Math.min(hint+8,hi);i++)
        if(track[i].t>t) return i-1;
    }
  }
  while(lo<hi){ const mid=(lo+hi+1)>>1; if(track[mid].t<=t) lo=mid; else hi=mid-1; }
  return lo;
}

function haverKm(lat1,lon1,lat2,lon2){
  const R=6371,p=Math.PI/180;
  const dLat=(lat2-lat1)*p, dLon=(lon2-lon1)*p;
  const a=Math.sin(dLat/2)**2+Math.cos(lat1*p)*Math.cos(lat2*p)*Math.sin(dLon/2)**2;
  return R*2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a));
}
function fmtT(s){const h=Math.floor(s/3600),m=Math.floor((s%3600)/60),sc=Math.floor(s%60);return`${h}:${pad(m)}:${pad(sc)}`;}
function fmtDur(s){const h=Math.floor(s/3600),m=Math.floor((s%3600)/60);return h?`${h}h ${pad(m)}m`:`${m}m`;}
function pad(n){return String(n).padStart(2,'0');}
function setLoad(msg){document.getElementById('load-msg').textContent=msg;}


const NM10 = 18.52; // km

// buildShelterMap: builds _shelter3Map keyed by base/objective key.
// Shelter3 units in ACMI are matched to known locations (from CAMPAIGN_GEODATA)

function buildShelterMap(){
  _shelter3Map={};
  if(!_merged) return;
  const shelters=[];
  for(const [id,obj] of Object.entries(_merged.objects)){
    if(obj.name!=='Shelter3') continue;
    const track=_merged.tracks[id];
    if(!track||!track.length) continue;
    shelters.push({id,obj,pt:track[0],startT:track[0].t,endT:track[track.length-1].t});
  }
  if(!shelters.length) return;

  const campaignId = _merged?._campaignId;
  const geodataBases = campaignId ? (CAMPAIGN_GEODATA.bases[campaignId]||[]) : [];
  const geodataObjs  = campaignId ? (CAMPAIGN_GEODATA.objectives[campaignId]||[]) : [];

  function registerLocation(lat, lon, key, fallbackCoal){
    const nearby = shelters
      .filter(sh => haverKm(lat, lon, sh.pt.lat, sh.pt.lon) < NM10)
      .sort((a,b) => a.startT - b.startT);
    const initialCoal = nearby.length ? nearby[0].obj.coalition : (fallbackCoal||'Neutral');
    _shelter3Map[key] = { shelterHistory: nearby, initialCoal };
  }

  for(const b of geodataBases)
    registerLocation(b.lat, b.lon, 'airbase_'+b.name, 'Neutral');
  for(const o of geodataObjs){
    const key = o.code ? o.code+'_'+o.name : 'obj_'+o.name;
    registerLocation(o.lat, o.lon, key, 'Neutral');
  }
}

function buildGroundKillTimes(){
  // Pre-populate kill times and hide times at load so seeking works correctly.
  // groundKillTimes: kill events only — these still drive explosion animations.
  // unitHideTimes:   Visible=0 timestamp if present, otherwise falls back to kill time.
  //                  Used for fade/hide logic. Never triggers explosions.
  for(const k of Object.keys(groundKillTimes)) delete groundKillTimes[k];
  for(const k of Object.keys(baseKillTimes)) delete baseKillTimes[k];
  for(const k of Object.keys(unitHideTimes)) delete unitHideTimes[k];
  if(!_merged) return;

  // Pass 1: record Visible=0 times from object metadata for all ground/SAM units
  for(const [id, obj] of Object.entries(_merged.objects)){
    const vt = obj.visible_off_t;
    if(vt == null) continue;
    if(isGroundVehicle(obj)){
      unitHideTimes[id] = vt;
    }
  }

  // Pass 2: record kill event times (unchanged — still drive explosions)
  for(const ev of _merged.events){
    if(ev.type!=='kill') continue;
    if(!ev.victim_id) continue;
    const victimObj = _merged.objects[ev.victim_id];
    if(!victimObj) continue;
    if(isGroundVehicle(victimObj)){
      // groundKillTimes is kill-events only (explosion trigger)
      if(!(ev.victim_id in groundKillTimes)) groundKillTimes[ev.victim_id] = ev.t;
      // unitHideTimes falls back to kill time if no Visible=0 was recorded
      if(!(ev.victim_id in unitHideTimes)) unitHideTimes[ev.victim_id] = ev.t;
    }
    // Factories killed
    const vnm = victimObj.name || '';
    if(vnm === 'Factory3'){
      const bkey = `factory_${ev.victim_id}`;
      if(!(bkey in baseKillTimes)) baseKillTimes[bkey] = ev.t;
    }
    // FARPs killed
    if(vnm === 'Shelter3FARP'){
      const track = _merged.tracks[ev.victim_id];
      if(track && track.length){
        const pt = track[0];
        const gk = `${pt.lat.toFixed(3)},${pt.lon.toFixed(3)}`;
        const fkey = `farp_${gk}`;
        if(!(fkey in baseKillTimes)) baseKillTimes[fkey] = ev.t;
      }
    }
  }

  // Pass 3: Visible=0 on Shelter3FARP / Factory3 — use as removal time when no kill event fired
  for(const [id, obj] of Object.entries(_merged.objects)){
    const vt = obj.visible_off_t;
    if(vt == null) continue;
    if(obj.name === 'Shelter3FARP'){
      const track = _merged.tracks[id];
      if(!track || !track.length) continue;
      const gk = `${track[0].lat.toFixed(3)},${track[0].lon.toFixed(3)}`;
      const fkey = `farp_${gk}`;
      if(!(fkey in baseKillTimes) || vt < baseKillTimes[fkey]) baseKillTimes[fkey] = vt;
    } else if(obj.name === 'Factory3'){
      const bkey = `factory_${id}`;
      if(!(bkey in baseKillTimes) || vt < baseKillTimes[bkey]) baseKillTimes[bkey] = vt;
    }
  }
}

function baseOwnerAt(key,t){
  const entry=_shelter3Map[key];
  if(!entry) return 'Neutral';
  const hist=entry.shelterHistory||[];
  if(!hist.length) return entry.initialCoal||'Neutral';
  // Walk history: each shelter is active from its startT until the next shelter appears (or end).
  // The owner at time t is the coalition of the last shelter whose startT <= t+30.
  let owner=entry.initialCoal||'Neutral';
  for(const sh of hist){
    if(t >= sh.startT - 30) owner=sh.obj.coalition;
    else break;
  }
  return owner;
}


//  UNIT INIT
// ════════════════════════════════════════════════════════════════════
const STRUCT_NAMES = new Set([
  'FARPWatchtower','FARP Flag','FARP Tanker','Shelter3','Shelter3FARP',
  'Shelter3Construction','Shelter3Crate','Windsock','JTACTower','FARPAmmoStatic','FatCowFuelTruck',
  'COMP RELOAD','Factory3','FactoryBuild','FactoryBuild3',
]);

// Aircraft-type prefixes used in ACMI unit names — used to exclude real aircraft
// from the ai_air SAM detection rule (e.g. 'FA-18C', 'CH-47D', 'An-30M')
const AIRCRAFT_PREFIXES = new Set(['FA','CH','An','UH','AH','Mi','Ka','Su','MiG','Tu','IL','A','B']);
// Standalone SAM/radar units with no group prefix in their ACMI name
const SAM_STANDALONE = new Set(['55G6 EWR','Dog Ear radar','SA-2 Fan Song','Flat Face radar',
  'P-19 Flat Face B','Spoon Rest','Side Net']);
// AI aircraft whose ACMI names don't follow a clear prefix pattern — explicit allowlist
const AI_AIRCRAFT_NAMES = new Set(['E2-D','KC-135']);

// Auto-detect SAM/air-defence units without a fixed whitelist.
// Ground units are shown by blacklist (see isGroundVehicle).
// ai_air non-human: show if name has a group prefix (e.g. 'SA10-S-300PS 5P85C ln')
// that is NOT an aircraft type prefix, OR is a known standalone radar.
function isSAMUnit(obj){
  if(!obj.name) return false;
  if(obj.category!=='ai_air') return false;
  if(obj.is_human) return false;
  const nm = obj.name;
  if(nm.toLowerCase().includes('truck build')) return false;
  // Explicit AI aircraft allowlist — never treat as SAM
  if(AI_AIRCRAFT_NAMES.has(nm)) return false;
  if(SAM_STANDALONE.has(nm)) return true;
  const dashIdx = nm.indexOf('-');
  if(dashIdx < 1) return false;
  const prefix = nm.slice(0, dashIdx);
  if(AIRCRAFT_PREFIXES.has(prefix)) return false;
  if(/^[A-Z]-?$/.test(prefix)) return false;
  return true;
}

// Strip group prefix for display: 'BDREDMRSAM-SA-11 Buk LN 9A310M1' → 'SA-11 Buk LN 9A310M1'
function samDisplayName(nm){
  const dashIdx = nm.indexOf('-');
  if(dashIdx > 0 && !SAM_STANDALONE.has(nm)){
    const prefix = nm.slice(0, dashIdx);
    if(!AIRCRAFT_PREFIXES.has(prefix) && !/^[A-Z]-?$/.test(prefix))
      return nm.slice(dashIdx+1);
  }
  return nm;
}

// For ground vehicles: show all real vehicles (not structures), excluding 'Base' callsigns
function isGroundVehicle(obj){
  if(!obj.name) return false;
  // ai_air SAM components (prefixed group names like 'SA10-S-300PS 5P85C ln')
  if(isSAMUnit(obj)) return true;
  // Everything below: ground category only
  if(obj.category!=='ground') return false;
  const nm=obj.name;
  // Exclude known structures and logistics clutter
  if(STRUCT_NAMES.has(nm)) return false;
  // Exclude BD/SA10/SA11 prefixed ground spawn markers
  if(nm.startsWith('BD')||nm.startsWith('SA11-')||nm.startsWith('SA10-')) return false;
  return true;
}

// For aircraft: show all player_air and ai_air with a name and track.
// Excludes SAM components (handled by isSAMUnit/isGroundVehicle).
function isNamedAircraft(obj){
  if(!obj.name) return false;
  if(obj.category!=='player_air'&&obj.category!=='ai_air') return false;
  // SAM components filed as ai_air are handled as ground units
  if(isSAMUnit(obj)) return false;
  return true;
}


async function initBases(merged, campaignId){
  // Store campaignId on merged so buildShelterMap (called before this) can also use it
  merged._campaignId = campaignId;

  let bases=[];
  if(SDCS_API){
    try{
      const r=await fetch(SDCS_API);const d=await r.json();
      bases=d.map(b=>({
        name:b.name||b.id,code:b.code||'',lat:parseFloat(b.lat||b.latitude),
        lon:parseFloat(b.lon||b.longitude),coalition:b.coalition||'Neutral',
        type:b.type||'objective',isFarp:false,isFactory:false,key:b.code||b.id,
      }));
    }catch(e){console.warn('SDCS API unavailable');}
  }

  if(!bases.length && CAMPAIGN_GEODATA){
    // ── Airbases — directly from CAMPAIGN_GEODATA.bases (DB coords, fixed positions)
    for(const b of (CAMPAIGN_GEODATA.bases[campaignId]||[])){
      const key='airbase_'+b.name;
      const initialCoal = _shelter3Map[key]?.initialCoal || 'Neutral';
      bases.push({key, name:b.name, code:'', lat:b.lat, lon:b.lon,
        coalition:initialCoal, type:'airbase', isFarp:false, isFactory:false});
    }

    // ── Objectives — directly from CAMPAIGN_GEODATA.objectives (DB coords, fixed positions)
    // Skip objectives whose name duplicates a base — they display as bases already
    const baseNameSet = new Set((CAMPAIGN_GEODATA.bases[campaignId]||[]).map(b => b.name.toLowerCase()));
    for(const o of (CAMPAIGN_GEODATA.objectives[campaignId]||[])){
      if(baseNameSet.has(o.name.toLowerCase())) continue;
      const key = o.code ? o.code+'_'+o.name : 'obj_'+o.name;
      const initialCoal = _shelter3Map[key]?.initialCoal || 'Neutral';
      bases.push({key, name:o.name, code:o.code||'', lat:o.lat, lon:o.lon,
        coalition:initialCoal, type:'objective', isFarp:false, isFactory:false});
    }

    // ── FARPs — Shelter3FARP units from ACMI (location from track data)
    const seenFarp=new Set();
    for(const [id,obj] of Object.entries(merged.objects)){
      if(obj.name!=='Shelter3FARP') continue;
      const track=merged.tracks[id];if(!track||!track.length) continue;
      const pt=track[0];
      const gk=`${pt.lat.toFixed(3)},${pt.lon.toFixed(3)}`;
      if(seenFarp.has(gk)) continue; seenFarp.add(gk);
      let farpName='FARP';
      for(const st of merged.statics){
        if(!st.name||!st.name.match(/^FARP\s+[RB]\d+/i)) continue;
        if(haverKm(st.lat,st.lon,pt.lat,pt.lon)<3){farpName=st.name;break;}
      }
      const key='farp_'+gk;
      bases.push({key,name:farpName,code:'',lat:pt.lat,lon:pt.lon,
        coalition:obj.coalition,type:'farp',isFarp:true,isFactory:false,
        firstSeen:obj.first_seen||pt.t});
    }

    // ── Factories — Factory3 units from ACMI (location from track data)
    for(const [id,obj] of Object.entries(merged.objects)){
      if(obj.name !== 'Factory3') continue;
      const track=merged.tracks[id];if(!track||!track.length) continue;
      const pt=track[0];
      const key=`factory_${id}`;
      bases.push({key,name:'Factory',code:'',lat:pt.lat,lon:pt.lon,
        coalition:obj.coalition,type:'factory',isFarp:false,isFactory:true,
        firstSeen:obj.first_seen||pt.t});
    }
  }

  _baseList=bases.map(b=>({key:b.key,name:b.name,lat:b.lat,lon:b.lon,
    coalition:b.coalition,isFarp:b.isFarp,isFactory:b.isFactory||false,
    firstSeen:b.firstSeen||0}));

  for(const b of bases) drawBase(b);
}

function drawBase(b){
  if(!b.lat||!b.lon) return;
  const blue=b.coalition==='Friendlies'||b.coalition==='Blue';
  const red=b.coalition==='Hostiles'||b.coalition==='Red';
  const teamColor=blue?'#58a6ff':red?'#f85149':'#888888';
  const isFarp=b.isFarp||b.type==='farp';
  const isAB=b.type==='airbase';
  const isFactory=b.isFactory||b.type==='factory';

  // Icon
  let shp;
  if(isFarp){
    shp=`<svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 11 11">
      <polygon points="5.5,0 11,5.5 5.5,11 0,5.5" fill="${teamColor}" opacity=".9"/>
      <polygon points="5.5,2.5 8.5,5.5 5.5,8.5 2.5,5.5" fill="${teamColor}" opacity=".35"/>
    </svg>`;
  } else if(isFactory){
    // Factory: gear-ish square with cross
    shp=`<svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 11 11">
      <rect x="1" y="1" width="9" height="9" rx="1.5" fill="${teamColor}" opacity=".85"/>
      <line x1="5.5" y1="1" x2="5.5" y2="10" stroke="#000" stroke-width=".8" opacity=".5"/>
      <line x1="1" y1="5.5" x2="10" y2="5.5" stroke="#000" stroke-width=".8" opacity=".5"/>
      <rect x="3.5" y="3.5" width="4" height="4" rx=".5" fill="none" stroke="#000" stroke-width=".8" opacity=".4"/>
    </svg>`;
  } else if(isAB){
    shp=`<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 13 13">
      <rect x="1" y="1" width="11" height="11" rx="2" fill="${teamColor}" opacity=".9"/>
      <line x1="6.5" y1="1" x2="6.5" y2="12" stroke="#000" stroke-width=".8" opacity=".4"/>
      <line x1="1" y1="6.5" x2="12" y2="6.5" stroke="#000" stroke-width=".8" opacity=".4"/>
    </svg>`;
  } else {
    shp=`<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 10 10">
      <polygon points="5,0 10,5 5,10 0,5" fill="${teamColor}" opacity=".85"/>
    </svg>`;
  }
  const sz=isAB?13:11;
  const icon=L.divIcon({html:shp,className:'',iconSize:[sz,sz],iconAnchor:[sz/2,sz/2]});
  const tip=isFarp?`<b>FARP</b>${b.name&&b.name!=='FARP'?' · '+b.name:''}`
    :isFactory?`<b>Factory</b>${b.name!=='Factory'?' · '+b.name:''}`
    :`<b>${b.name}</b>${b.code?' ['+b.code+']':''}`;
  const mk=L.marker([b.lat,b.lon],{icon,zIndexOffset:-600});
  mk.bindTooltip(`${tip}<br>${blue?'🔵 Blue':'🔴 Red'} · ${b.type}`,{direction:'top',offset:[0,-5]});
  if(filters.bases) mk.addTo(map);
  baseMarkers[b.key]=mk;

  // Circle: factories use green fill, others use team colour
  const circFill=isFactory?'#44cc44':teamColor;
  const circFillOp=isFactory?0.06:0.05;
  const circR=18520; // 10nm for all: objectives, FARPs, and factories
  const circ=L.circle([b.lat,b.lon],{
  radius:circR,pane:'basePane',
  color:teamColor,weight:2,opacity:0.75,
  fillColor:circFill,fillOpacity:circFillOp*1.5,interactive:false,
  });
  if(filters.bases) circ.addTo(map);
  baseCircles[b.key]=circ;

  // Inner concentric ring — airbases only
  if(isAB){
    // Inner ring sits 2px gap inside outer stroke — approximate in metres
    const innerR = circR - 800; // ~800m = visual 2px gap at zoom 7
    const innerCirc = L.circle([b.lat,b.lon],{
      radius:innerR, pane:'basePane',
      color:teamColor, weight:1.5, opacity:0.50,
      fill:false, interactive:false,
    });
    if(filters.bases) innerCirc.addTo(map);
    baseInnerCircles[b.key]=innerCirc;
  }

  // Name label on map (bases & factories, not FARPs)
  if(!isFarp){
    const clr=blue?'blue':red?'red':'neutral';
    // Objectives: prepend code to label unless name already starts with it (e.g. 'FK34 Crossroads')
  const labelName=(!isFactory&&!isFarp&&b.code&&!b.name.startsWith(b.code))?`${b.code} ${b.name}`:b.name;
  const displayName=isFactory?`⚙ ${b.name}`:labelName;
    const lblHtml=isFactory
      ?`<div class="blabel-name ${clr}" style="font-size:12px;font-style:italic">${displayName}</div>`
      :`<div class="blabel-name ${clr}">${displayName}</div>`;
    const lbl=L.divIcon({html:lblHtml,className:'blabel',iconSize:[200,18],iconAnchor:[0,-sz/2-4]});
    const lblMk=L.marker([b.lat,b.lon],{icon:lbl,pane:'blabelPane',interactive:false});
    if(filters.bases) lblMk.addTo(map);
    baseLabels[b.key]=lblMk;
  }
}


function isWpn(n){
  if(!n) return false;
  const u = n.toUpperCase();
  // parse_acmi prefixes weapon objects with 'weapons.' or 'weapons.shells.' etc.
  if(u.startsWith('WEAPONS.') || u.startsWith('WEAPONS/')) return true;
  return ['AGM','AIM','MIM','AAM','HARM','HELLFIRE','HYDRA','ZUNI','MK-','GBU-','JDAM',
          'R-','S-5','S-8','S-13','S-24','KH-','X-','C-701','CM-','SD-10'].some(w=>u.includes(w));
}

// Add a kill to the feed
function addKillFeedEntry(ev, t){
  const killerCs=(ev.killer||'').trim();
  if(!killerCs||/^\d+/.test(killerCs)) return; // non-player killer

  const killerCoal=playerColors[killerCs]? (playerColors[killerCs]==='#58a6ff'?'Friendlies':'Hostiles') : null;
  const victimIsPlayer=ev.victim_category==='player_air'&&ev.victim_pilot;
  const victimCs=(ev.victim_pilot||'').replace(/\s*\(\d+\)$/,'').trim();
  const pvp=victimIsPlayer&&victimCs&&!/^\d+/.test(victimCs);

  const victimName=victimIsPlayer?victimCs:(ev.victim_name||'Unknown');
  const weaponName=(ev.weapon||'?').replace(/_/g,' ');

  const list=document.getElementById('killfeed-list');
  // Remove placeholder
  const ph=list.querySelector('div[style]');if(ph)ph.remove();
  // Cap feed at 60 entries — remove oldest from top
  if(killFeedEntries.length>=60){
    const oldest=killFeedEntries.shift();
    if(oldest.el.parentNode) oldest.el.parentNode.removeChild(oldest.el);
  }

  const el=document.createElement('div');
  el.className='kf-row';
  if(pvp){
    const blue=killerCoal==='Friendlies';
    el.classList.add(blue?'pvp-blue':'pvp-red');
  }
  const killerColor=playerColors[killerCs]||'#aaa';
  const timeStr=fmtT(t);
  // Find what aircraft the killer was in at kill time
  let killerAc = '';
  if(_merged && _merged._dp && _merged._dp[killerCs]){
    const flights = _merged._dp[killerCs].flights || [];
    const ev_t = ev.t;
    const flight = flights.find(f => ev_t >= f.start_t && ev_t <= (f.end_t + 60) && f.aircraft && !isWpn(f.aircraft));
    if(flight) killerAc = flight.aircraft.replace(/_/g,' ');
  }
  const esc=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  const killerLine = killerAc
    ? `<span class="kf-killer" style="color:${killerColor}">${esc(killerCs)}</span> <span class="kf-ac">(${esc(killerAc)})</span>`
    : `<span class="kf-killer" style="color:${killerColor}">${esc(killerCs)}</span>`;
  el.innerHTML=`<span class="kf-time">${timeStr}</span>
    ${killerLine} killed<br>
    <span class="kf-victim">${esc(victimName)}</span><br>
    <span class="kf-weapon">${esc(weaponName)}</span>`;

  // Insert at top
  list.insertBefore(el,list.firstChild);

  // Fade out after 10 minutes of game time
  killFeedEntries.push({t:ev.t,el});
}

function updateKillFeed(t){
  const FADE_SECS=600; // 10 min
  for(const entry of killFeedEntries){
    const age=t-entry.t;
    if(age>FADE_SECS){
      entry.el.style.opacity='0';
      entry.el.style.pointerEvents='none';
    } else if(age<0){
      entry.el.style.opacity='0';
      entry.el.style.pointerEvents='none';
    } else {
      entry.el.style.opacity='1';
      entry.el.style.pointerEvents='';
    }
  }
}


function spawnExp(lat,lon,isPlayer){
  const sz=isPlayer?58:34,dur=isPlayer?1800:1200;
  const fc=isPlayer?'#ff4422':'#ffaa22';
  const ring=isPlayer?'#ff8844':'#ffcc44';
  const smoke=isPlayer?'#886655':'#998866';
  const h=sz/2;
  const sparks=[0,45,90,135,180,225,270,315].map(a=>{
    const r=h*.55,r2=h*.82;
    const x1=(Math.cos(a*Math.PI/180)*r).toFixed(1),y1=(Math.sin(a*Math.PI/180)*r).toFixed(1);
    const x2=(Math.cos(a*Math.PI/180)*r2).toFixed(1),y2=(Math.sin(a*Math.PI/180)*r2).toFixed(1);
    return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${ring}" stroke-width="${isPlayer?2.5:1.5}" stroke-linecap="round"/>`;
  }).join('');
  const html=`<div style="position:relative;width:${sz}px;height:${sz}px;pointer-events:none">
    <div style="position:absolute;left:50%;top:50%;width:${sz*.9}px;height:${sz*.9}px;border-radius:50%;border:${isPlayer?4:3}px solid ${smoke};animation:er2 ${dur}ms ease-out forwards"></div>
    <div style="position:absolute;left:50%;top:50%;width:${sz*.75}px;height:${sz*.75}px;border-radius:50%;border:${isPlayer?5:3}px solid ${ring};background:radial-gradient(circle,${fc}cc 0%,${fc}55 50%,transparent 75%);animation:er1 ${dur*.8}ms ease-out forwards"></div>
    <div style="position:absolute;left:50%;top:50%;width:${sz*.4}px;height:${sz*.4}px;border-radius:50%;background:radial-gradient(circle,#ffffcc 0%,#ffdd44 40%,${fc} 80%);animation:ec ${dur*.7}ms ease-out forwards;box-shadow:0 0 ${isPlayer?18:10}px #ffaa33"></div>
    <svg style="position:absolute;left:50%;top:50%;overflow:visible;animation:esk ${dur*.9}ms ease-out forwards" width="${sz}" height="${sz}" viewBox="-${h} -${h} ${sz} ${sz}">${sparks}</svg>
  </div>`;
  const icon=L.divIcon({html,className:'expmark',iconSize:[sz,sz],iconAnchor:[h,h]});
  const m=L.marker([lat,lon],{icon,zIndexOffset:5000,interactive:false}).addTo(map);
  killLayers.push(m);
  setTimeout(()=>{try{map.removeLayer(m)}catch(e){}},dur+100);
}


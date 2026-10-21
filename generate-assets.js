const fs = require('fs');
const path = require('path');

const outDir = path.join(__dirname, 'frontend', 'public', 'images');
if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

function createSvg(width, height, content) {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}">
${content}
</svg>`;
}

const assets = {
  'jamdani-saree.svg': createSvg(800, 600, `
    <defs>
      <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#4A0E17"/>
        <stop offset="50%" stop-color="#80182A"/>
        <stop offset="100%" stop-color="#2D060C"/>
      </linearGradient>
      <pattern id="goldMotif" width="60" height="60" patternUnits="userSpaceOnUse">
        <polygon points="30,5 35,22 52,22 38,32 44,48 30,38 16,48 22,32 8,22 25,22" fill="#F59E0B" opacity="0.35"/>
        <circle cx="30" cy="30" r="4" fill="#F59E0B" opacity="0.8"/>
      </pattern>
    </defs>
    <rect width="800" height="600" fill="url(#bg)"/>
    <rect width="800" height="600" fill="url(#goldMotif)"/>
    <!-- Saree Drape Geometry -->
    <path d="M 120,600 C 180,350 320,180 500,120 C 650,70 760,180 800,240 L 800,600 Z" fill="#991B1B" opacity="0.85"/>
    <path d="M 220,600 C 290,400 450,260 620,220 C 730,190 780,260 800,320 L 800,600 Z" fill="#B91C1C" opacity="0.9"/>
    <!-- Jamdani Gold Zari Pallu Border -->
    <line x1="50" y1="520" x2="750" y2="520" stroke="#F59E0B" stroke-width="8" stroke-dasharray="16,8"/>
    <line x1="50" y1="535" x2="750" y2="535" stroke="#F59E0B" stroke-width="4"/>
    <line x1="50" y1="545" x2="750" y2="545" stroke="#F59E0B" stroke-width="12" stroke-dasharray="8,4"/>
    <!-- Label -->
    <text x="400" y="580" fill="#FFFFFF" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="20" letter-spacing="4" text-anchor="middle" opacity="0.9">AUTHENTIC DHAKAI JAMDANI</text>
  `),

  'linen-kurti.svg': createSvg(800, 600, `
    <defs>
      <linearGradient id="kurtiBg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#1E293B"/>
        <stop offset="100%" stop-color="#0F172A"/>
      </linearGradient>
      <linearGradient id="fabric" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#0284C7"/>
        <stop offset="100%" stop-color="#0369A1"/>
      </linearGradient>
    </defs>
    <rect width="800" height="600" fill="url(#kurtiBg)"/>
    <!-- Kurti Silhouette -->
    <path d="M 320,120 L 360,200 L 440,200 L 480,120 L 590,210 L 520,290 L 510,540 L 290,540 L 280,290 L 210,210 Z" fill="url(#fabric)"/>
    <!-- Embroidered Neckline & Placket -->
    <path d="M 360,200 Q 400,260 440,200 L 415,360 L 385,360 Z" fill="#F8FAFC" opacity="0.95"/>
    <circle cx="400" cy="240" r="3" fill="#D97706"/>
    <circle cx="400" cy="275" r="3" fill="#D97706"/>
    <circle cx="400" cy="310" r="3" fill="#D97706"/>
    <circle cx="400" cy="345" r="3" fill="#D97706"/>
    <text x="400" y="580" fill="#94A3B8" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="18" letter-spacing="3" text-anchor="middle">DESIGNER LINEN 3-PIECE KURTI SET</text>
  `),

  'luxury-watch.svg': createSvg(800, 600, `
    <defs>
      <linearGradient id="watchBg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#0A0B0E"/>
        <stop offset="100%" stop-color="#161A23"/>
      </linearGradient>
      <radialGradient id="emeraldDial" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stop-color="#059669"/>
        <stop offset="65%" stop-color="#064E3B"/>
        <stop offset="100%" stop-color="#022C22"/>
      </radialGradient>
      <linearGradient id="steelCase" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#E2E8F0"/>
        <stop offset="30%" stop-color="#94A3B8"/>
        <stop offset="70%" stop-color="#CBD5E1"/>
        <stop offset="100%" stop-color="#64748B"/>
      </linearGradient>
    </defs>
    <rect width="800" height="600" fill="url(#watchBg)"/>
    <!-- Steel Bracelet Links (Top & Bottom) -->
    <rect x="330" y="20" width="140" height="120" rx="8" fill="url(#steelCase)"/>
    <rect x="330" y="460" width="140" height="120" rx="8" fill="url(#steelCase)"/>
    <line x1="330" y1="70" x2="470" y2="70" stroke="#475569" stroke-width="2"/>
    <line x1="330" y1="520" x2="470" y2="520" stroke="#475569" stroke-width="2"/>
    <!-- Watch Case -->
    <circle cx="400" cy="300" r="175" fill="url(#steelCase)"/>
    <!-- Outer Bezel with Tachymeter -->
    <circle cx="400" cy="300" r="150" fill="#0F172A" stroke="#E2E8F0" stroke-width="4"/>
    <!-- Sunburst Emerald Dial -->
    <circle cx="400" cy="300" r="132" fill="url(#emeraldDial)"/>
    <!-- Chronograph Subdials -->
    <circle cx="355" cy="300" r="28" fill="#022C22" stroke="#10B981" stroke-width="1.5"/>
    <circle cx="445" cy="300" r="28" fill="#022C22" stroke="#10B981" stroke-width="1.5"/>
    <circle cx="400" cy="345" r="28" fill="#022C22" stroke="#10B981" stroke-width="1.5"/>
    <!-- Hour Markers & Hands -->
    <circle cx="400" cy="300" r="120" stroke="#FFFFFF" stroke-width="2" stroke-dasharray="2,29.4" fill="none"/>
    <!-- Hour Hand -->
    <line x1="400" y1="300" x2="340" y2="250" stroke="#F8FAFC" stroke-width="6" stroke-linecap="round"/>
    <!-- Minute Hand -->
    <line x1="400" y1="300" x2="465" y2="210" stroke="#F8FAFC" stroke-width="4" stroke-linecap="round"/>
    <!-- Emerald Second Hand -->
    <line x1="400" y1="320" x2="400" y2="185" stroke="#10B981" stroke-width="2" stroke-linecap="round"/>
    <circle cx="400" cy="300" r="6" fill="#F8FAFC"/>
    <!-- Crown & Pushers -->
    <rect x="575" y="285" width="22" height="30" rx="4" fill="url(#steelCase)"/>
    <rect x="560" y="235" width="18" height="20" rx="3" fill="url(#steelCase)"/>
    <rect x="560" y="345" width="18" height="20" rx="3" fill="url(#steelCase)"/>
    <text x="400" y="240" fill="#F8FAFC" font-family="'Oswald', sans-serif" font-weight="700" font-size="14" letter-spacing="4" text-anchor="middle">CHRONOS SWISS</text>
    <text x="400" y="258" fill="#10B981" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="10" letter-spacing="2" text-anchor="middle">AUTOMATIC · 100M</text>
  `),

  'retro-keyboard.svg': createSvg(800, 600, `
    <defs>
      <linearGradient id="kbBg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#0F172A"/>
        <stop offset="100%" stop-color="#020617"/>
      </linearGradient>
      <linearGradient id="caseGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#E2E8F0"/>
        <stop offset="100%" stop-color="#CBD5E1"/>
      </linearGradient>
    </defs>
    <rect width="800" height="600" fill="url(#kbBg)"/>
    <!-- Keyboard Chassis -->
    <rect x="140" y="140" width="520" height="320" rx="20" fill="url(#caseGrad)" stroke="#94A3B8" stroke-width="4"/>
    <rect x="160" y="160" width="480" height="280" rx="12" fill="#1E293B"/>
    <!-- Keycap Rows (Stylized 75% Layout) -->
    ${Array.from({ length: 5 }).map((_, r) => {
      return Array.from({ length: 13 }).map((_, c) => {
        const x = 180 + c * 34;
        const y = 180 + r * 50;
        const isAccent = (r === 0 && c === 0) || (r === 4 && c === 12) || (r === 2 && c === 12);
        const fill = isAccent ? '#10B981' : (r === 0 ? '#334155' : '#F1F5F9');
        const textFill = isAccent ? '#000000' : '#475569';
        return `<rect x="${x}" y="${y}" width="30" height="42" rx="6" fill="${fill}" stroke="#0F172A" stroke-width="1.5"/>`;
      }).join('');
    }).join('')}
    <!-- Rotary Encoder Knob -->
    <circle cx="615" cy="195" r="15" fill="#D97706" stroke="#92400E" stroke-width="2"/>
    <text x="400" y="520" fill="#94A3B8" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="18" letter-spacing="3" text-anchor="middle">KEYCRAFT 75% WIRELESS MECHANICAL KEYBOARD</text>
  `),

  'sunset-lamp.svg': createSvg(800, 600, `
    <defs>
      <radialGradient id="sunsetHalo" cx="50%" cy="40%" r="45%">
        <stop offset="0%" stop-color="#FEF08A"/>
        <stop offset="35%" stop-color="#F59E0B"/>
        <stop offset="65%" stop-color="#EF4444"/>
        <stop offset="85%" stop-color="#831843"/>
        <stop offset="100%" stop-color="#0A0B0E" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <rect width="800" height="600" fill="#0A0B0E"/>
    <!-- Glowing Sunset Projection Circle -->
    <circle cx="400" cy="260" r="230" fill="url(#sunsetHalo)"/>
    <!-- Lamp Silhouette -->
    <circle cx="400" cy="260" r="50" fill="#0F172A" stroke="#38BDF8" stroke-width="4"/>
    <circle cx="400" cy="260" r="42" fill="#38BDF8" opacity="0.3"/>
    <!-- Stand -->
    <rect x="394" y="310" width="12" height="180" fill="#1E293B"/>
    <ellipse cx="400" cy="490" rx="70" ry="16" fill="#0F172A" stroke="#334155" stroke-width="2"/>
    <text x="400" y="550" fill="#F59E0B" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="18" letter-spacing="3" text-anchor="middle">AURA 16-COLOR RGB SUNSET PROJECTION LAMP</text>
  `),

  'urban-sneakers.svg': createSvg(800, 600, `
    <defs>
      <linearGradient id="snkBg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#18181B"/>
        <stop offset="100%" stop-color="#09090B"/>
      </linearGradient>
    </defs>
    <rect width="800" height="600" fill="url(#snkBg)"/>
    <!-- Streetwear Low-Top Sneaker Silhouette -->
    <path d="M 170,390 L 190,320 C 230,280 290,260 360,250 L 420,240 C 470,240 510,270 540,310 C 580,350 630,360 660,370 L 660,420 C 660,435 640,440 600,440 L 200,440 C 170,440 160,420 170,390 Z" fill="#E4E4E7"/>
    <!-- Suede Accent Overlays -->
    <path d="M 180,390 C 210,340 260,310 320,300 L 320,430 L 190,430 Z" fill="#71717A"/>
    <path d="M 520,310 C 560,340 610,360 655,370 L 655,420 L 520,420 Z" fill="#71717A"/>
    <!-- Signature Stripe -->
    <path d="M 330,320 C 400,320 480,360 560,410 L 530,425 C 460,380 390,345 330,345 Z" fill="#10B981"/>
    <!-- Sole & Cushion Line -->
    <rect x="160" y="420" width="510" height="35" rx="8" fill="#FFFFFF" stroke="#D4D4D8" stroke-width="2"/>
    <text x="400" y="520" fill="#A1A1AA" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="18" letter-spacing="3" text-anchor="middle">URBAN SUEDE & LEATHER STREETWEAR SNEAKERS</text>
  `),

  'barista-espresso.svg': createSvg(800, 600, `
    <defs>
      <linearGradient id="espBg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#1C1917"/>
        <stop offset="100%" stop-color="#0C0A09"/>
      </linearGradient>
      <linearGradient id="cylinder" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stop-color="#44403C"/>
        <stop offset="40%" stop-color="#78716C"/>
        <stop offset="70%" stop-color="#A8A29E"/>
        <stop offset="100%" stop-color="#292524"/>
      </linearGradient>
    </defs>
    <rect width="800" height="600" fill="url(#espBg)"/>
    <!-- Cylindrical Portable Espresso Machine -->
    <rect x="330" y="100" width="140" height="340" rx="24" fill="url(#cylinder)"/>
    <!-- Power Button & LED Ring -->
    <circle cx="400" cy="220" r="22" fill="#1C1917" stroke="#10B981" stroke-width="3"/>
    <circle cx="400" cy="220" r="10" fill="#10B981"/>
    <!-- Pressure Extraction Nozzle & Cup -->
    <rect x="360" y="440" width="80" height="30" rx="4" fill="#1C1917"/>
    <path d="M 350,470 L 450,470 L 435,530 L 365,530 Z" fill="#FAFAF9" stroke="#E7E5E4" stroke-width="2"/>
    <text x="400" y="570" fill="#D6D3D1" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="18" letter-spacing="3" text-anchor="middle">BARISTA PRO PORTABLE USB-C 15-BAR ESPRESSO MAKER</text>
  `),

  'old-money-shirt.svg': createSvg(800, 600, `
    <defs>
      <linearGradient id="shBg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#1F2937"/>
        <stop offset="100%" stop-color="#111827"/>
      </linearGradient>
    </defs>
    <rect width="800" height="600" fill="url(#shBg)"/>
    <!-- Cuban Collar Shirt Silhouette -->
    <path d="M 280,140 L 360,210 L 440,210 L 520,140 L 610,230 L 550,290 L 540,520 L 260,520 L 250,290 L 190,230 Z" fill="#F8FAFC"/>
    <!-- Open Cuban Lapels -->
    <polygon points="360,210 330,280 400,290" fill="#E2E8F0"/>
    <polygon points="440,210 470,280 400,290" fill="#E2E8F0"/>
    <!-- Natural Shell Buttons -->
    <circle cx="400" cy="340" r="5" fill="#CBD5E1" stroke="#94A3B8"/>
    <circle cx="400" cy="400" r="5" fill="#CBD5E1" stroke="#94A3B8"/>
    <circle cx="400" cy="460" r="5" fill="#CBD5E1" stroke="#94A3B8"/>
    <text x="400" y="565" fill="#94A3B8" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="18" letter-spacing="3" text-anchor="middle">OLD MONEY TEXTURED CUBAN COLLAR LINEN SHIRT</text>
  `),

  'cotton-panjabi.svg': createSvg(800, 600, `
    <defs>
      <linearGradient id="pjBg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#18181B"/>
        <stop offset="100%" stop-color="#09090B"/>
      </linearGradient>
    </defs>
    <rect width="800" height="600" fill="url(#pjBg)"/>
    <!-- Panjabi Silhouette -->
    <path d="M 310,100 L 360,170 L 440,170 L 490,100 L 590,220 L 530,270 L 520,540 L 280,540 L 270,270 L 210,220 Z" fill="#F4F4F5"/>
    <!-- Mandarin/Band Collar -->
    <path d="M 360,170 C 380,185 420,185 440,170 L 435,145 C 415,155 385,155 365,145 Z" fill="#E4E4E7"/>
    <!-- Embroidered Button Placket -->
    <rect x="390" y="180" width="20" height="150" fill="#D4D4D8" stroke="#A1A1AA" stroke-width="1"/>
    <circle cx="400" cy="205" r="3" fill="#D97706"/>
    <circle cx="400" cy="240" r="3" fill="#D97706"/>
    <circle cx="400" cy="275" r="3" fill="#D97706"/>
    <circle cx="400" cy="310" r="3" fill="#D97706"/>
    <text x="400" y="575" fill="#A1A1AA" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="18" letter-spacing="3" text-anchor="middle">PREMIUM EGYPTIAN GIZA COTTON PANJABI</text>
  `),

  'iphone-18.svg': createSvg(800, 600, `
    <defs>
      <linearGradient id="iphBg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#0F172A"/>
        <stop offset="100%" stop-color="#020617"/>
      </linearGradient>
      <linearGradient id="titanium" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#94A3B8"/>
        <stop offset="50%" stop-color="#64748B"/>
        <stop offset="100%" stop-color="#334155"/>
      </linearGradient>
    </defs>
    <rect width="800" height="600" fill="url(#iphBg)"/>
    <!-- Titanium Body -->
    <rect x="290" y="80" width="220" height="440" rx="36" fill="url(#titanium)" stroke="#CBD5E1" stroke-width="4"/>
    <rect x="296" y="86" width="208" height="428" rx="32" fill="#020617"/>
    <!-- Dynamic Island -->
    <rect x="365" y="105" width="70" height="18" rx="9" fill="#000000" stroke="#334155" stroke-width="1"/>
    <!-- OLED Display Glow -->
    <circle cx="400" cy="300" r="60" fill="#38BDF8" opacity="0.15"/>
    <text x="400" y="310" fill="#F8FAFC" font-family="'Oswald', sans-serif" font-weight="700" font-size="28" letter-spacing="4" text-anchor="middle">IPHONE 18 PRO</text>
    <text x="400" y="340" fill="#10B981" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="12" letter-spacing="3" text-anchor="middle">TITANIUM NATURAL</text>
    <text x="400" y="565" fill="#64748B" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="18" letter-spacing="3" text-anchor="middle">APPLE IPHONE 18 PRO MAX (256GB)</text>
  `),

  's24-ultra.svg': createSvg(800, 600, `
    <defs>
      <linearGradient id="s24Bg" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#020617"/>
        <stop offset="100%" stop-color="#0F172A"/>
      </linearGradient>
    </defs>
    <rect width="800" height="600" fill="url(#s24Bg)"/>
    <!-- Boxy Sharp Titanium Edge -->
    <rect x="280" y="80" width="240" height="440" rx="14" fill="#334155" stroke="#94A3B8" stroke-width="4"/>
    <rect x="286" y="86" width="228" height="428" rx="10" fill="#020617"/>
    <!-- Punch-hole Camera -->
    <circle cx="400" cy="110" r="6" fill="#000000" stroke="#1E293B" stroke-width="1"/>
    <!-- Display Glow -->
    <circle cx="400" cy="300" r="70" fill="#A855F7" opacity="0.15"/>
    <text x="400" y="305" fill="#F8FAFC" font-family="'Oswald', sans-serif" font-weight="700" font-size="26" letter-spacing="3" text-anchor="middle">S24 ULTRA</text>
    <text x="400" y="335" fill="#A855F7" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="12" letter-spacing="3" text-anchor="middle">GALAXY AI IS HERE</text>
    <text x="400" y="565" fill="#64748B" font-family="'Plus Jakarta Sans', sans-serif" font-weight="700" font-size="18" letter-spacing="3" text-anchor="middle">SAMSUNG GALAXY S24 ULTRA (12/256GB)</text>
  `),

  'billboard-jamdani.svg': createSvg(1200, 600, `
    <defs>
      <linearGradient id="bb1" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#4C0519"/>
        <stop offset="50%" stop-color="#881337"/>
        <stop offset="100%" stop-color="#0A0B0E"/>
      </linearGradient>
      <pattern id="jamdaniMotifLg" width="80" height="80" patternUnits="userSpaceOnUse">
        <polygon points="40,10 48,30 70,30 52,44 58,66 40,52 22,66 28,44 10,30 32,30" fill="#F59E0B" opacity="0.3"/>
        <circle cx="40" cy="40" r="5" fill="#F59E0B" opacity="0.7"/>
      </pattern>
    </defs>
    <rect width="1200" height="600" fill="url(#bb1)"/>
    <rect width="1200" height="600" fill="url(#jamdaniMotifLg)"/>
    <line x1="0" y1="500" x2="1200" y2="500" stroke="#F59E0B" stroke-width="12" stroke-dasharray="24,12"/>
  `),

  'billboard-watch.svg': createSvg(1200, 600, `
    <defs>
      <linearGradient id="bb2" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#022C22"/>
        <stop offset="50%" stop-color="#064E3B"/>
        <stop offset="100%" stop-color="#0A0B0E"/>
      </linearGradient>
    </defs>
    <rect width="1200" height="600" fill="url(#bb2)"/>
    <!-- Giant Emerald Dial Arc -->
    <circle cx="950" cy="300" r="360" fill="#047857" opacity="0.25"/>
    <circle cx="950" cy="300" r="300" fill="#065F46" opacity="0.4"/>
    <circle cx="950" cy="300" r="240" fill="#022C22" stroke="#10B981" stroke-width="4"/>
    <circle cx="950" cy="300" r="220" stroke="#FFFFFF" stroke-width="3" stroke-dasharray="3,40" fill="none"/>
  `),

  'billboard-tech.svg': createSvg(1200, 600, `
    <defs>
      <linearGradient id="bb3" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#0F172A"/>
        <stop offset="50%" stop-color="#1E293B"/>
        <stop offset="100%" stop-color="#0A0B0E"/>
      </linearGradient>
    </defs>
    <rect width="1200" height="600" fill="url(#bb3)"/>
    <!-- Dynamic Glowing Titanium Bevels -->
    <circle cx="900" cy="300" r="280" fill="#38BDF8" opacity="0.12"/>
    <rect x="750" y="80" width="300" height="520" rx="40" fill="#1E293B" stroke="#64748B" stroke-width="4" opacity="0.6"/>
  `)
};

for (const [filename, content] of Object.entries(assets)) {
  fs.writeFileSync(path.join(outDir, filename), content.trim());
}

console.log('Successfully generated all ' + Object.keys(assets).length + ' local SVG assets!');


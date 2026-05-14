import os
import sys
import django
from datetime import timedelta, date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from clubs.models import Club
from events.models import Event, EventRequest

User = get_user_model()
now = timezone.now()

print("=" * 60)
print("BUBT UniEvents — Add Events Script")
print("=" * 60)

# ── Helper ──────────────────────────────────────────────────
def make_slug(title):
    slug = slugify(title)
    base = slug; ctr = 1
    while Event.objects.filter(slug=slug).exists():
        slug = f"{base}-{ctr}"; ctr += 1
    return slug

def create_event(club_name, title, etype, venue, desc, short,
                 start_offset_days, duration_days,
                 is_free=True, fee=0,
                 status='published', max_p=100,
                 reg_open_offset=-7, reg_close_offset=None):
    """
    start_offset_days:
      negative  → অতীত (past)
      0 বা small negative/positive → ongoing
      positive  → upcoming (future)
    """
    club = Club.objects.filter(name=club_name).first()
    if not club:
        print(f"  ⚠  Club not found: {club_name}")
        return None

    start = now + timedelta(days=start_offset_days)
    end   = start + timedelta(days=duration_days)
    reg_open  = now + timedelta(days=reg_open_offset)
    reg_close = (end if reg_close_offset is None
                 else now + timedelta(days=reg_close_offset))

    event = Event.objects.create(
        title=title,
        slug=make_slug(title),
        description=desc,
        short_description=short,
        club=club,
        event_type=etype,
        venue=venue,
        start_date=start,
        end_date=end,
        is_free=is_free,
        fee=fee,
        max_participants=max_p,
        status=status,
        is_featured=False,
        created_by=club.president,
        registration_open=reg_open,
        registration_close=reg_close,
    )
    return event

# ════════════════════════════════════════════════════════════
# SECTION 1 — UPCOMING EVENTS (প্রতিটি club এ 1 টি)
# ════════════════════════════════════════════════════════════
print("\n[1/3] Creating upcoming events (1 per club)...")

UPCOMING = [
    (
        'BUBT EEE Club',
        'Smart Home IoT Workshop 2026', 'workshop',
        'BUBT EEE Lab, Building C, Room 301',
        'Hands-on workshop on building smart home automation systems using ESP32, Arduino, and Raspberry Pi. '
        'Participants will design and program real IoT devices including smart lights, door locks, and temperature '
        'controllers. Each team will take home their assembled prototype. Prior programming knowledge recommended '
        'but not strictly required. The workshop runs across one full day with morning theory and afternoon lab sessions.',
        'Build real IoT smart-home devices — take your assembled prototype home.',
        20, 1, False, 300
    ),
    (
        'BUBT Rover Scout Group',
        'Disaster Preparedness & First Aid Camp 2026', 'workshop',
        'BUBT Open Ground & Health Center',
        'Two-day camp focusing on disaster preparedness, emergency first aid, search-and-rescue basics, and '
        'community service skills. Certified trainers from the Bangladesh Red Crescent Society will lead sessions. '
        'Participants learn CPR, wound care, fire safety, and flood rescue techniques. Completion certificate '
        'from Bangladesh Scouts issued to all participants who pass the final assessment.',
        'Certified first aid and disaster-preparedness training from Red Crescent trainers.',
        25, 2, False, 200
    ),
    (
        'BUBT IT Club',
        'Web Development Bootcamp 2026', 'workshop',
        'BUBT Computer Lab, Building B, 2nd Floor',
        'Three-day intensive bootcamp covering modern full-stack web development using HTML5, CSS3, JavaScript, '
        'React, and Node.js. Participants build a complete web application from scratch under expert guidance. '
        'Industry mentors from leading Bangladeshi software companies provide real-world project feedback. '
        'Certificates issued to all who complete the project. Suitable for beginners and intermediate developers.',
        '3-day full-stack bootcamp — build a real web app with industry mentors.',
        18, 3, False, 500, 100
    ),
    (
        'BUBT Business Club',
        'Leadership & Negotiation Skills Summit 2026', 'seminar',
        'BUBT Conference Hall, 5th Floor',
        'Full-day leadership summit featuring keynote addresses and interactive workshops from senior executives '
        'of top Bangladeshi companies. Topics include negotiation tactics, conflict resolution, executive presence, '
        'and strategic decision-making under uncertainty. Panel discussion on women in leadership in Bangladesh. '
        'Networking lunch with speakers included. CPD certificate issued to all registered participants.',
        'One-day leadership summit with top executives — networking lunch included.',
        22, 1, True, 0, 80
    ),
    (
        'BUBT Cultural Club',
        'Eid Cultural Celebration 2026', 'social',
        'BUBT Main Auditorium',
        'Annual Eid cultural celebration featuring traditional musical performances, poetry recitation, '
        'folk dance, and drama. All BUBT departments compete in separate cultural categories. Special '
        'performances by invited artists. Traditional food stalls and photo booth areas set up around '
        'the campus. The event runs from 2 PM to 10 PM with a grand finale performance and prize-giving ceremony.',
        'Annual Eid cultural gala — performances, competitions, and traditional food.',
        30, 1, True, 0, 500
    ),
    (
        'BUBT Sports Club',
        'Inter-Department Football Tournament 2026', 'competition',
        'BUBT Football Field & Sports Complex',
        'Annual inter-department football tournament in a knockout format. Ten department teams compete over '
        'three weekends. Each match is 90 minutes with standard FIFA rules. Referees are licensed by the '
        'Bangladesh Football Federation. Championship trophy, individual Best Player, and Top Scorer awards '
        'will be presented at the closing ceremony. Spectators from all departments are welcome.',
        'Annual 10-team inter-department football — licensed referees, 3-weekend knockout.',
        14, 1, True, 0, 200
    ),
    (
        'BUBT English Language Club',
        'Public Speaking & Confidence Workshop 2026', 'workshop',
        'BUBT Seminar Hall, 4th Floor',
        'One-day workshop designed to help students overcome stage fright and develop powerful public speaking '
        'skills. Activities include impromptu speaking, storytelling, debate practice, and one-on-one coaching '
        'sessions with experienced trainers. Video recording and playback exercises help participants identify '
        'areas for improvement. Participation certificate issued to all attendees.',
        'Overcome stage fright and build speaking confidence — with video feedback coaching.',
        16, 1, True, 0, 60
    ),
    (
        'BUBT Photography Club',
        'Portrait Photography Masterclass 2026', 'workshop',
        'BUBT Photography Studio & Campus Grounds',
        'Full-day portrait photography masterclass led by a professional commercial photographer with 15 years '
        'of industry experience. Morning sessions cover lighting theory, composition, and camera settings. '
        'Afternoon sessions are practical shoots with live models and feedback. Participants bring their own '
        'cameras. Selected works will be exhibited in the club annual gallery and featured on club social media.',
        'Pro portrait photography masterclass — theory in the morning, live shoots in the afternoon.',
        19, 1, True, 0, 30
    ),
    (
        'BUBT Social Welfare Club',
        'Tree Plantation Drive & Environmental Awareness Walk 2026', 'social',
        'BUBT Campus and Mirpur Residential Area',
        'Full-day environmental initiative featuring a tree plantation drive across BUBT campus and the '
        'surrounding Mirpur residential area, followed by an awareness walk educating residents about '
        'environmental issues. Participants plant at least five trees each. Partnered with local government '
        'environmental department. Each participant receives a certificate of environmental contribution. '
        'Refreshments provided throughout the day.',
        'Plant trees and raise environmental awareness — certificate of contribution for all.',
        21, 1, True, 0, 150
    ),
    (
        'BUBT Debating Club',
        'Freshers Debate Tournament 2026', 'competition',
        'BUBT Seminar Hall A & B',
        'Annual debate tournament exclusively for first and second-year BUBT students new to competitive '
        'debating. Asian Parliamentary format used. Experienced senior debaters serve as mentors and coaches '
        'throughout the tournament. Motions drawn from current affairs, social issues, and campus life topics. '
        'Winners fast-tracked to the main BUBT debate team trials. Certificate of participation for all entrants.',
        'Freshers-only debate tournament — winners fast-tracked to main team trials.',
        17, 2, True, 0, 80
    ),
    (
        'BUBT Economics Club',
        'Research Paper Presentation Competition 2026', 'competition',
        'BUBT Conference Room, 5th Floor',
        'Annual student research paper competition on topics related to Bangladesh development economics, '
        'digital economy, and international trade. Papers reviewed by a panel of economics faculty and '
        'external researchers. Top three papers published in the club annual journal. Cash prizes of '
        'BDT 5,000, 3,000, and 2,000 for first, second, and third place respectively. Open to all BUBT students.',
        'Present your economics research — top papers published in the club annual journal.',
        23, 1, False, 100, 40
    ),
    (
        'IEEE Student Branch BUBT',
        'AI & Machine Learning Workshop Series 2026', 'workshop',
        'BUBT Computer Lab, Building B',
        'Four-session workshop series on applied Artificial Intelligence and Machine Learning using Python, '
        'TensorFlow, and scikit-learn. Sessions cover supervised learning, neural networks, computer vision, '
        'and NLP fundamentals. Each session includes hands-on Jupyter notebook exercises. Industry practitioners '
        'from leading AI companies in Bangladesh deliver guest lectures. IEEE membership certificate provided '
        'on completion of all four sessions.',
        '4-session applied AI/ML workshop — hands-on Python, TensorFlow, and NLP.',
        28, 4, False, 600, 50
    ),
    (
        'Bangladesh National Cadet Corps BUBT',
        'New Cadet Enrollment & Orientation 2026', 'other',
        'BUBT Open Ground & Assembly Hall',
        'Official new cadet enrollment and orientation program for the new academic year. Interested students '
        'undergo a physical fitness test, basic discipline assessment, and personal interview. Selected cadets '
        'receive their enrollment documents, uniform measurement appointments, and full schedule for the '
        'upcoming training year. Existing cadets assist in orientation and share their experiences. '
        'Parents and guardians are welcome to attend the orientation session.',
        'Enroll in BNCC — physical test, interview, and orientation for new cadets.',
        20, 2, True, 0, 100
    ),
    (
        'BUBT Moot Court Society',
        'Legal Research & Advocacy Skills Training 2026', 'workshop',
        'BUBT Moot Court Room, Law Department',
        'Two-day intensive training on legal research methodology, memorial drafting, and oral advocacy '
        'techniques for moot court competitions. Trainers include practicing advocates and a retired judge. '
        'Participants work on a sample moot problem with full supervision and feedback. A mock oral argument '
        'round is held on day two before an experienced bench. Certificate of completion issued to all who '
        'finish both days. Open exclusively to registered BUBT law students.',
        'Expert-led moot training — research, memorial drafting, and mock oral arguments.',
        15, 2, False, 250, 40
    ),
    (
        'BASIS Students Forum BUBT Chapter',
        'Startup Bangladesh Bootcamp 2026', 'workshop',
        'BUBT Entrepreneurship Lab, 6th Floor',
        'Three-day startup bootcamp in partnership with Startup Bangladesh, the government tech startup '
        'initiative. Participants learn lean startup methodology, MVP development, business model canvas, '
        'and startup funding strategies. Mentors from active Bangladeshi startups guide each team. '
        'Top teams get referred to Startup Bangladesh incubation program for official consideration. '
        'Open to all BUBT students regardless of department.',
        '3-day startup bootcamp — top teams referred to Startup Bangladesh incubation.',
        26, 3, True, 0, 60
    ),
]

upcoming_count = 0
for row in UPCOMING:
    ev = create_event(*row)
    if ev:
        print(f"  ✓  Upcoming: {ev.title[:55]}")
        upcoming_count += 1

print(f"  → {upcoming_count} upcoming events created.")

# ════════════════════════════════════════════════════════════
# SECTION 2 — EXTRA ONGOING EVENTS (6 টি club এ)
# ════════════════════════════════════════════════════════════
print("\n[2/3] Creating ongoing events (6 clubs)...")

ONGOING = [
    (
        'BUBT IT Club',
        'Google Developer Study Jam 2026', 'workshop',
        'BUBT Computer Lab, Building B, Room 205',
        'A 5-day Google-sponsored study jam focusing on Google Cloud Platform, Firebase, and Flutter. '
        'Participants complete guided labs on Google Cloud Skills Boost and earn digital skill badges. '
        'Free Google Cloud credits provided to all registered participants. Daily quizzes with prizes '
        'for top performers. Completion badge and certificate from Google Developer Student Clubs issued.',
        '5-day Google Cloud study jam — earn digital skill badges and free cloud credits.',
        -2, 5, True, 0
    ),
    (
        'BUBT Cultural Club',
        'Annual Drama Rehearsal Week 2026', 'social',
        'BUBT Auditorium Stage & Rehearsal Rooms',
        'Week-long open rehearsal and casting period for the annual BUBT cultural drama production. '
        'Students from all departments are invited to audition for acting, stage management, set design, '
        'lighting, and sound roles. Professional theatre director guiding the production. Final show '
        'scheduled for next month in the main auditorium. This is the production rehearsal open week.',
        'Open auditions and rehearsal week for the annual BUBT drama production.',
        -3, 7, True, 0
    ),
    (
        'BUBT Sports Club',
        'Badminton Singles Championship 2026', 'competition',
        'BUBT Indoor Sports Hall, Ground Floor',
        'Round-robin and knockout badminton singles championship open to all BUBT students. '
        'Competition runs across five days with morning and evening match slots. Badminton '
        'Federration-certified referee officiating all matches. Trophy, medals, and sports vouchers '
        'for champion and runner-up. Spectator stands available. Faculty members have a separate '
        'category running parallel to the main student competition.',
        '5-day badminton singles championship — separate student and faculty categories.',
        -1, 5, True, 0
    ),
    (
        'BUBT Debating Club',
        'Weekly Debate Practice Sessions — Spring 2026', 'meeting',
        'BUBT Seminar Room 3B',
        'Weekly structured debate practice sessions running every Monday and Thursday throughout the '
        'spring semester. Each session focuses on a different debate skill: argument construction, '
        'rebuttal techniques, POI handling, and delivery. All skill levels welcome from complete '
        'beginners to experienced debaters. Experienced senior members and coaches facilitate each '
        'session. Attendance log maintained for club records and team selection consideration.',
        'Weekly practice sessions every Mon/Thu — all skill levels welcome.',
        -1, 90, True, 0
    ),
    (
        'IEEE Student Branch BUBT',
        'PCB Design & Electronics Project Exhibition 2026', 'other',
        'BUBT Electronics Lab & Exhibition Corridor',
        'Three-day PCB design and electronics project exhibition where IEEE members showcase ongoing '
        'semester projects including microcontroller-based automation, sensor systems, and IoT prototypes. '
        'Visitors can interact with working prototypes and receive technical explanations from project '
        'teams. Industry judges evaluate projects on innovation, technical depth, and presentation. '
        'Best project awards and certificates presented at the closing ceremony on day three.',
        '3-day live electronics project showcase — interact with working prototypes.',
        -1, 3, True, 0
    ),
    (
        'BUBT Economics Club',
        'Spring 2026 Economics Seminar Series', 'seminar',
        'BUBT Conference Hall, 5th Floor',
        'Ongoing weekly economics seminar series running throughout the spring semester. Each week a '
        'guest speaker — economist, policymaker, or researcher — presents on a current economic topic '
        'related to Bangladesh. Topics include monetary policy, trade policy, climate finance, digital '
        'economy, and poverty reduction. Open to all BUBT students. Attendance certificate provided '
        'to students who attend at least five sessions across the series.',
        'Weekly economics seminars — attend 5+ sessions for an attendance certificate.',
        -2, 60, True, 0
    ),
]

ongoing_count = 0
for row in ONGOING:
    ev = create_event(*row)
    if ev:
        print(f"  ✓  Ongoing:  {ev.title[:55]}")
        ongoing_count += 1

print(f"  → {ongoing_count} ongoing events created.")

# ════════════════════════════════════════════════════════════
# SECTION 3 — PAST EVENTS (সব club এ 1-2 টি করে)
# ════════════════════════════════════════════════════════════
print("\n[3/3] Creating past events...")

PAST = [
    # EEE Club
    ('BUBT EEE Club', 'EEE Day 2025', 'social',
     'BUBT Main Campus & Open Ground',
     'Annual EEE Day celebration featuring project exhibitions, guest lectures from industry professionals, '
     'equipment demonstrations, and cultural performances by EEE students. Over 400 students and faculty '
     'attended the event. Guest speakers from Grameenphone and BPDB delivered keynote addresses on the '
     'future of electrical engineering in Bangladesh. Best project awards presented in five categories.',
     'Annual EEE Day — project expo, industry keynotes, and cultural performances.',
     -120, 1, True, 0),

    ('BUBT EEE Club', 'Electronics Olympiad Winter 2025', 'competition',
     'BUBT EEE Lab, Building C',
     'Electronics and circuit design olympiad for EEE and CSE students. 120 participants competed in '
     'theory, practical circuit troubleshooting, and rapid-prototype rounds. Top three winners received '
     'cash prizes and advanced to the inter-university electronics competition. Event co-sponsored by '
     'Bangladesh Electronic Importers and Merchants Association.',
     '120-participant electronics olympiad — theory, troubleshooting, and rapid-prototype rounds.',
     -90, 2, False, 200),

    # Rover Scout
    ('BUBT Rover Scout Group', 'National Scout Jamboree Participation 2025', 'other',
     'National Scout Jamboree Ground, Gazipur',
     'BUBT Rover Scout Group participated in the National Scout Jamboree alongside scouts from across '
     'Bangladesh. Our group won the Best New Unit Award for discipline and community service contributions. '
     'Rovers participated in adventure activities, leadership challenges, and cultural exchange programs '
     'with international scout delegations. Full report and photos published in the university newsletter.',
     'BUBT Rovers won Best New Unit at the National Scout Jamboree in Gazipur.',
     -150, 5, False, 500),

    # IT Club
    ('BUBT IT Club', 'HackBUBT 2025 — Annual Hackathon', 'competition',
     'BUBT Computer Lab, Building B — All Floors',
     '24-hour hackathon with 50 teams competing to build working software solutions for real-world problems '
     'in healthcare, agriculture, and fintech. Sponsored by BJIT Group and Kona Software Lab. Grand prize '
     'of BDT 1,00,000 awarded to the winning team whose project was later accepted into a startup '
     'incubation program. Over 200 participants and 30 industry mentors participated.',
     '24-hour hackathon — 50 teams, BDT 1 lakh prize, real startup problem statements.',
     -100, 2, True, 0),

    ('BUBT IT Club', 'Cybersecurity Awareness Seminar 2025', 'seminar',
     'BUBT Auditorium',
     'Half-day cybersecurity awareness seminar covering phishing attacks, social engineering, password '
     'security, and safe internet practices. Delivered by a certified ethical hacker from BASIS. Live '
     'demonstration of common attack vectors and defenses. 300+ students and faculty attended. '
     'Free cybersecurity resource pack distributed to all attendees.',
     'Live hacking demos and cybersecurity training from a certified ethical hacker.',
     -60, 1, True, 0),

    # Business Club
    ('BUBT Business Club', 'Entrepreneurship Summit BUBT 2025', 'conference',
     'BUBT Conference Hall & Lobby',
     'Full-day entrepreneurship summit featuring 12 successful Bangladeshi entrepreneurs sharing their '
     'journeys and business insights. Startup pitch competition with BDT 50,000 seed money prize. '
     'Investors from Bangladesh Angels Network attended and held one-on-one sessions with selected '
     'teams. Over 350 students participated in the event. Media coverage from national newspapers.',
     'Entrepreneurship summit — 12 founders, pitch competition, BDT 50k prize.',
     -80, 1, True, 0),

    # Cultural Club
    ('BUBT Cultural Club', 'BUBT Annual Cultural Night 2025', 'social',
     'BUBT Main Auditorium',
     'Grand annual cultural night featuring performances by all 15 BUBT departments. Categories included '
     'folk music, classical dance, drama, stand-up comedy, and fashion show. Attended by over 1,500 '
     'students, faculty, and guests. Headline performance by a popular Bangladeshi folk band. '
     'Covered by six national media outlets. Best Performance awards given in each category.',
     'Grand annual cultural night — 1,500+ attendees, performances by all 15 departments.',
     -110, 1, True, 0),

    ('BUBT Cultural Club', 'Independence Day Cultural Program 2025', 'social',
     'BUBT Main Campus Grounds',
     'Special cultural program celebrating Bangladesh Independence Day on March 26th. Program included '
     'flag hoisting, national anthem, patriotic songs, poetry recitation, and a photo exhibition on '
     'the Liberation War. Faculty, staff, and all students participated. A documentary screening on '
     'the 1971 Liberation War was held in the auditorium following the outdoor ceremonies.',
     'Independence Day program — flag hoisting, patriotic performances, Liberation War documentary.',
     -40, 1, True, 0),

    # Sports Club
    ('BUBT Sports Club', 'BUBT Annual Sports Day 2025', 'competition',
     'BUBT Sports Complex and Open Ground',
     'Full-day annual sports day featuring track and field events, tug-of-war, relay races, and '
     'three-on-three basketball. 500+ students from all departments participated. Department points '
     'tally kept across all events with the championship trophy awarded to CSE department. Refreshments '
     'and first aid provided. Attended by university chancellor, vice-chancellor, and senior faculty.',
     'Annual sports day — 500+ participants, track & field, basketball, and tug-of-war.',
     -130, 1, True, 0),

    # English Language Club
    ('BUBT English Language Club', 'National Debate Invitational 2025', 'competition',
     'BUBT Auditorium & Seminar Halls',
     'Two-day inter-university debate competition in British Parliamentary format attracting teams from '
     '20 universities across Bangladesh. BUBT team reached the semi-finals. Expert adjudicators from '
     'the Bangladesh Debate Federation officiated. Best Speaker award won by a BUBT student. Media '
     'coverage in leading national daily newspapers.',
     'Inter-university BP debate — 20 universities, BUBT reached the semis.',
     -70, 2, True, 0),

    # Photography Club
    ('BUBT Photography Club', 'Annual Photo Exhibition — Lens & Life 2025', 'social',
     'BUBT Exhibition Gallery & Main Corridor',
     'Annual photo exhibition featuring 200 curated photographs taken by BUBT Photography Club members '
     'throughout the year. Categories included portrait, street, nature, architecture, and documentary. '
     'Exhibition remained open for five days and was viewed by over 800 students and faculty. '
     'Guest judges from the Bangladesh Photographic Society awarded prizes in each category.',
     '200-photo annual exhibition viewed by 800+ visitors — judged by national photography society.',
     -85, 5, True, 0),

    # Social Welfare
    ('BUBT Social Welfare Club', 'Winter Blanket Distribution Drive 2025', 'social',
     'Mirpur Low-Income Residential Area, Dhaka',
     'Winter relief drive distributing 500 blankets to low-income families in the Mirpur area. '
     'Organized in partnership with BUBT Administration and supported by faculty donations. '
     'Volunteers from all clubs participated. Media coverage by three national television channels. '
     'BUBT allocated additional budget following the success and visibility of the initiative.',
     'Distributed 500 blankets to Mirpur low-income families — all clubs volunteered.',
     -140, 1, True, 0),

    # Debating Club
    ('BUBT Debating Club', 'BUBT Internal Debate Championship 2025', 'competition',
     'BUBT Seminar Hall A & B',
     'Annual internal debate championship exclusively for BUBT students. Asian Parliamentary format '
     'used across preliminary rounds with British Parliamentary for the semi-finals and final. '
     '32 teams participated across two days. The championship final was judged by a High Court '
     'advocate. The winning team represented BUBT in the subsequent national inter-university '
     'debate championship.',
     '32-team internal championship — winners represented BUBT nationally.',
     -95, 2, True, 0),

    # Economics Club
    ('BUBT Economics Club', 'Bangladesh Budget Response Seminar 2025', 'seminar',
     'BUBT Conference Hall, 5th Floor',
     'Post-budget analysis seminar held immediately after the national budget announcement. Economics '
     'faculty and guest economists analyzed budget allocations, tax policies, and development expenditure. '
     'Student panel presented responses from a youth perspective. Live questions from 250 attendees. '
     'Event streamed live on BUBT Economics Club YouTube channel reaching 2,000 online viewers.',
     'Post-budget analysis with economists — streamed live to 2,000 online viewers.',
     -115, 1, True, 0),

    # IEEE
    ('IEEE Student Branch BUBT', 'IEEE Day 2025 Celebration', 'social',
     'BUBT Engineering Building, All Floors',
     'IEEE Day global celebration event at BUBT featuring technical quiz competitions, project demos, '
     'and a networking dinner with IEEE senior members. Special talks on the history of IEEE and the '
     'importance of international professional engineering societies. New member induction ceremony '
     'conducted. BUBT IEEE Branch received the Best Student Branch Activity recognition from IEEE Bangladesh Section.',
     'IEEE Day celebration — quizzes, demos, induction ceremony, and award from IEEE Bangladesh.',
     -55, 1, True, 0),

    # BNCC
    ('Bangladesh National Cadet Corps BUBT', 'Republic Day Parade Participation 2025', 'other',
     'National Parade Ground, Dhaka Cantonment',
     'BUBT BNCC unit participated in the national Republic Day parade on February 16th at the '
     'National Parade Ground. The unit was recognized for its exceptional drill discipline and '
     'awarded a commendation certificate from the BNCC Directorate. Cadet officers were also '
     'acknowledged individually by the reviewing General Officer Commanding.',
     'BUBT BNCC received a Directorate commendation at the national Republic Day parade.',
     -45, 1, True, 0),

    # Moot Court
    ('BUBT Moot Court Society', 'Jessup Moot Court Bangladesh National Rounds 2025', 'competition',
     'Dhaka, National Rounds Venue',
     'BUBT Moot Court Society competed in the Philip C. Jessup International Law Moot Court '
     'Competition Bangladesh National Rounds. Our team advanced to the semi-finals — the best '
     'result in BUBT history. The memorial submitted by BUBT received the Best Applicant Memorial '
     'award. The team will advance to the international rounds pending funding confirmation.',
     'BUBT reached Jessup semis and won Best Memorial — best result in university history.',
     -160, 3, False, 800),

    # BASIS
    ('BASIS Students Forum BUBT Chapter', 'ICT Career Expo BUBT 2025', 'social',
     'BUBT Ground Floor Lobby & Main Corridors',
     'Bi-annual ICT career expo with 25 BASIS member companies hosting booths for on-spot interviews '
     'and internship recruitment. 450 BUBT students attended. 38 students received on-spot interview '
     'call letters and 12 internship offers were issued on the day of the event. Post-event survey '
     'confirmed an 84% student satisfaction rating. The expo has grown 40% in company participation '
     'compared to the previous edition.',
     '25 ICT companies, 38 interview call letters, 12 internship offers issued on the day.',
     -75, 1, True, 0),
]

past_count = 0
for row in PAST:
    ev = create_event(*row, status='completed',
                      reg_open_offset=row[6]-10,   # reg_open = 10 days before event
                      reg_close_offset=row[6]+1)    # reg_close = day after start
    if ev:
        print(f"  ✓  Past:     {ev.title[:55]}")
        past_count += 1

print(f"  → {past_count} past events created.")

# ════════════════════════════════════════════════════════════
# SECTION 4 — DRAFT EVENTS + ADMIN APPROVAL REQUESTS (2 টি)
# ════════════════════════════════════════════════════════════
print("\n[4/4] Creating 2 draft events with admin approval requests...")

DRAFT_EVENTS = [
    (
        'BUBT IT Club',
        'National Hackathon HackBUBT 2026', 'competition',
        'BUBT Computer Labs, Building B — All Floors',
        '36-hour national-level hackathon open to university students across Bangladesh. Teams of 3-4 '
        'work on problem statements from fintech, healthtech, and edtech sectors provided by industry '
        'sponsors. Prize pool of BDT 2,00,000. Mentors from leading tech companies available round '
        'the clock. Three finalist teams receive startup mentorship from BASIS. Online qualifier '
        'preceding the on-site final event.',
        'National 36-hour hackathon — BDT 2 lakh prize, mentor access, startup pathway.',
        45, 2, True, 0
    ),
    (
        'BUBT Cultural Club',
        'BUBT Freshers Welcome Night 2026', 'social',
        'BUBT Main Auditorium & Campus Grounds',
        'Grand welcome night for newly enrolled BUBT students. Program includes cultural performances '
        'by senior students, a welcome address from university leadership, club fair where all 15 clubs '
        'set up recruitment stalls, music, refreshments, and a raffle draw with prizes. The event aims '
        'to help freshers make connections, discover club opportunities, and feel welcomed into the '
        'BUBT community on their very first large campus event.',
        'Grand freshers welcome night — cultural shows, club fair, refreshments, raffle prizes.',
        40, 1, True, 0
    ),
]

admin_user = (
    User.objects.filter(user_type='admin').first()
    or User.objects.filter(is_staff=True).first()
    or User.objects.filter(is_superuser=True).first()
)

request_count = 0
for row in DRAFT_EVENTS:
    ev = create_event(*row, status='draft')
    if ev:
        # Check if a request already exists
        if not EventRequest.objects.filter(event=ev).exists():
            er = EventRequest.objects.create(
                event=ev,
                requested_by=ev.club.president,
                status='pending',
                request_type='publish',
                admin_note='',
            )
            print(f"  ✓  Draft + Request: {ev.title[:45]}")
            print(f"       Club: {ev.club.name}")
            print(f"       Requested by: {ev.club.president.username}")
            request_count += 1

print(f"  → {request_count} event requests created (pending admin approval).")

# ════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════
from events.models import Event

upcoming_total  = Event.objects.filter(start_date__gt=now, status='published').count()
ongoing_total   = Event.objects.filter(start_date__lte=now, end_date__gte=now, status='published').count()
past_total      = Event.objects.filter(status='completed').count()
draft_total     = Event.objects.filter(status='draft').count()
pending_req     = EventRequest.objects.filter(status='pending').count()

print("\n" + "=" * 60)
print("DONE! Summary")
print("=" * 60)
print(f"  Upcoming events  : {upcoming_total}")
print(f"  Ongoing events   : {ongoing_total}")
print(f"  Past events      : {past_total}")
print(f"  Draft events     : {draft_total}")
print(f"  Pending requests : {pending_req}  (awaiting admin approval)")
print()
print("  Existing clubs, users, and members are UNTOUCHED.")
print("=" * 60)
print()
print("Admin panel এ যাও এবং Event Requests দেখো:")
print("  → Dashboard → Event Requests → Pending")
print()
print("দুটি pending request আছে:")
for er in EventRequest.objects.filter(status='pending'):
    print(f"  • {er.event.title}")
    print(f"    Requested by: {er.requested_by.username} ({er.event.club.name})")

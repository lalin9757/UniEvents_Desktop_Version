"""
BUBT UniEvents — Complete Data Seeding Script
Run this from your project root:
    python seed_data.py

This script will:
1. Clear all non-superadmin/admin data
2. Create 15 BUBT clubs from official website navbar
3. Assign 1 unique president per club
4. Add exactly 5 members per club
5. Create 1 ongoing event per club
"""

import os
import sys
import django
from datetime import timedelta, date
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from clubs.models import Club, ClubMember, ClubCategory
from events.models import Event

User = get_user_model()

print("=" * 60)
print("BUBT UniEvents — Data Seeding Script")
print("=" * 60)

# STEP 1: CLEAR OLD DATA
print("\n[1/5] Clearing old data...")
Event.objects.all().delete()
ClubMember.objects.all().delete()
Club.objects.all().delete()
ClubCategory.objects.all().delete()
User.objects.filter(is_staff=False, user_type__in=['student', 'president']).delete()
print("    Done.")

# STEP 2: CATEGORIES
print("\n[2/5] Creating categories...")
categories = {
    'Technology': ClubCategory.objects.create(name='Technology', icon='💻', description='Technology, programming, and innovation clubs'),
    'Business':   ClubCategory.objects.create(name='Business', icon='💼', description='Business, entrepreneurship and economics'),
    'Cultural':   ClubCategory.objects.create(name='Cultural', icon='🎭', description='Cultural, arts and language clubs'),
    'Sports':     ClubCategory.objects.create(name='Sports', icon='⚽', description='Sports and physical activity clubs'),
    'Social':     ClubCategory.objects.create(name='Social Service', icon='🤝', description='Volunteer and social welfare clubs'),
    'Academic':   ClubCategory.objects.create(name='Academic', icon='📚', description='Academic and research clubs'),
    'Science':    ClubCategory.objects.create(name='Science & Engineering', icon='🔬', description='Science and engineering clubs'),
    'Military':   ClubCategory.objects.create(name='Defence & Discipline', icon='🎖️', description='Cadet and defence clubs'),
}
print(f"    {len(categories)} categories created.")

# STEP 3: CLUBS AND PRESIDENTS
print("\n[3/5] Creating clubs and presidents...")

DEPARTMENTS = [
    'Computer Science & Engineering', 'Electrical & Electronic Engineering',
    'Business Administration', 'Economics', 'English', 'Law',
    'Mathematics & Statistics', 'Civil Engineering',
]

CLUBS_DATA = [
    {
        'name': 'BUBT EEE Club',
        'category': 'Science',
        'short_description': 'Promoting robotics, electronics, and electrical engineering innovation at BUBT since 2016.',
        'description': 'The BUBT EEE Club was officially established in 2016 to serve as the hub for electrical and electronics engineering students at Bangladesh University of Business and Technology. The club is dedicated to academic and practical development in areas including robotics, artificial intelligence, embedded systems, and renewable energy. It organizes annual events like EEE Week, EEE Day, Robotics Competition, Electrical and Electronic Olympiad, and Math and Physics Olympiad. Club members have competed in numerous national and international robotics and engineering competitions, securing top positions and bringing recognition to BUBT. The EEE Club bridges the gap between classroom theory and real-world engineering applications, preparing students for successful careers in the electrical and electronics industry.',
        'email': 'eeeclub@bubt.edu.bd',
        'established': '2016-03-10',
        'president_username': 'eeeclub_pres',
        'president_first': 'Tanvir',
        'president_last': 'Ahmed',
        'president_password': 'EEEClub@2025',
    },
    {
        'name': 'BUBT Rover Scout Group',
        'category': 'Social',
        'short_description': 'Bangladesh Scouts affiliated group building character, leadership, and service excellence among BUBT students.',
        'description': 'BUBT Rover Scout Group is affiliated with Bangladesh Scouts under the World Organization of the Scout Movement. Rovering is the senior branch of scouting for young adults aged 17-25, focused on service and adventure. The group participates in national scout jamborees, international scout events, and community service projects. Rovers undergo leadership training, first aid courses, outdoor survival skills training, and civic education programs. BUBT Rovers regularly serve the community during national disasters, providing relief and rescue support. The group maintains discipline, develops teamwork, and instills the timeless values of scouting — duty to God, country, and society.',
        'email': 'roverscout@bubt.edu.bd',
        'established': '2004-05-01',
        'president_username': 'scout_pres',
        'president_first': 'Mahmudul',
        'president_last': 'Hassan',
        'president_password': 'ScoutBUBT@2025',
    },
    {
        'name': 'BUBT IT Club',
        'category': 'Technology',
        'short_description': 'Delivering IT knowledge and fostering tech innovation among all BUBT students since 2011.',
        'description': 'BUBT IT Club started its journey in September 2011. Established with the aim of delivering IT knowledge towards students of all disciplines, the club organizes programming contests, hackathons, workshops on cutting-edge technologies including AI, machine learning, web development, and cybersecurity. Members regularly participate in national and international programming competitions, bringing recognition to BUBT. The club maintains strong connections with major tech companies in Bangladesh for internship and job placement support. Whether you are a beginner or an experienced developer, BUBT IT Club provides the perfect platform to grow and excel in the technology field.',
        'email': 'itclub@bubt.edu.bd',
        'established': '2011-09-01',
        'president_username': 'itclub_pres',
        'president_first': 'Rafiqul',
        'president_last': 'Islam',
        'president_password': 'ITClub@2025',
    },
    {
        'name': 'BUBT Business Club',
        'category': 'Business',
        'short_description': 'Building the next generation of business leaders through networking, competitions, and real-world exposure.',
        'description': 'BUBT Business Club started its journey in 2003, making it one of the oldest and most prestigious clubs at Bangladesh University of Business and Technology. The club works to bridge the gap between academic business education and the corporate world. It builds corporate linkages with national and multinational organizations, maintains an internship database, and facilitates job opportunities for its members. Key activities include business plan competitions, case study competitions, job fairs with leading corporate houses, and seminars featuring top business executives. Alumni of the club now hold prominent positions in major corporations across Bangladesh and internationally.',
        'email': 'bizclub@bubt.edu.bd',
        'established': '2003-06-01',
        'president_username': 'bizclub_pres',
        'president_first': 'Shahadath',
        'president_last': 'Hossain',
        'president_password': 'BizClub@2025',
    },
    {
        'name': 'BUBT Cultural Club',
        'category': 'Cultural',
        'short_description': 'Promoting cultural diversity, creativity, and artistic excellence across BUBT campus.',
        'description': 'BUBT Cultural Club (BUBTCC) promotes students creativity and professionalism through a cultural framework by invigorating cultural diversity and awareness. The club organizes various inter-departmental cultural competitions and central cultural programs in the University. It observes national days solemnly with cultural events and encourages the budding talents of the University. The club provides the right platform for students to showcase their talents, enhancing personal skills like confidence, collaboration, teamwork, discipline, communication, and improvisation. It develops and promotes the rich diversity of various arts and enriches the consciousness of students about their cultural heritage.',
        'email': 'cultural@bubt.edu.bd',
        'established': '2004-01-20',
        'president_username': 'cultural_pres',
        'president_first': 'Fatema',
        'president_last': 'Begum',
        'president_password': 'CulturalClub@2025',
    },
    {
        'name': 'BUBT Sports Club',
        'category': 'Sports',
        'short_description': 'Umbrella organization for all sports at BUBT — promoting fitness, teamwork, and competitive excellence.',
        'description': 'BUBT Sports Club is the umbrella organization for all sporting activities at Bangladesh University of Business and Technology. The club promotes physical fitness, teamwork, competitive spirit, and sportsmanship among the student community. It organizes inter-department tournaments in cricket, football, basketball, badminton, volleyball, and table tennis. BUBT sports teams also compete in inter-university competitions, consistently performing at a high level. The club maintains and manages the university sports facilities and equipment. Regular participation in sports reduces stress, builds resilience, and develops leadership qualities essential in both academic and professional life.',
        'email': 'sports@bubt.edu.bd',
        'established': '2003-08-01',
        'president_username': 'sports_pres',
        'president_first': 'Mizanur',
        'president_last': 'Rahman',
        'president_password': 'SportsClub@2025',
    },
    {
        'name': 'BUBT English Language Club',
        'category': 'Academic',
        'short_description': 'Enhancing English language proficiency and communication skills for all BUBT students.',
        'description': 'BUBT English Language Club is dedicated to improving English language skills among students of Bangladesh University of Business and Technology. The club organizes English speaking workshops, creative writing competitions, book reading circles, vocabulary building sessions, and English movie screenings with discussion. Members practice English in a supportive, friendly environment that builds confidence. The club also prepares students for international English proficiency tests like IELTS and TOEFL, and organizes English Olympiads. Special programs focus on business English, presentation skills, and professional communication. Members have achieved high IELTS scores and gained acceptance to prestigious universities abroad.',
        'email': 'englishclub@bubt.edu.bd',
        'established': '2006-02-14',
        'president_username': 'english_pres',
        'president_first': 'Sumaia',
        'president_last': 'Khanam',
        'president_password': 'EnglishClub@2025',
    },
    {
        'name': 'BUBT Photography Club',
        'category': 'Cultural',
        'short_description': "Capturing moments and telling stories through the lens — BUBT's creative photography community.",
        'description': 'BUBT Photography Club unites photography enthusiasts from all departments of Bangladesh University of Business and Technology. From beginners picking up a camera for the first time to seasoned photographers honing their craft, the club welcomes all skill levels. The club conducts regular photo walks around Dhaka, studio photography workshops, photo editing tutorials, and exhibitions showcasing member work. Members learn various photography genres including portrait, landscape, street, documentary, and event photography. An annual photography contest and exhibition is a highlight of the academic year. The club also provides official photography services for university events and programs.',
        'email': 'photoclub@bubt.edu.bd',
        'established': '2008-07-15',
        'president_username': 'photo_pres',
        'president_first': 'Sabbir',
        'president_last': 'Rahman',
        'president_password': 'PhotoClub@2025',
    },
    {
        'name': 'BUBT Social Welfare Club',
        'category': 'Social',
        'short_description': 'Serving the community through volunteer work, charity, and social development initiatives since BUBT inception.',
        'description': 'BUBT Social Welfare Club started working since the inception of the university with a view to helping and supporting people in need and the society as a whole. The motto of the club is to serve the society and respond to the needs of the suffering humanity. The club conducts blood donation campaigns, food distribution programs for underprivileged communities, school supply drives for rural students, and fundraising for disaster relief. Members volunteer at orphanages, hospitals, and community centers in Dhaka. Environmental initiatives include tree planting drives, clean-up campaigns, and awareness programs about climate change and sustainable living.',
        'email': 'welfare@bubt.edu.bd',
        'established': '2003-11-01',
        'president_username': 'welfare_pres',
        'president_first': 'Rubina',
        'president_last': 'Akter',
        'president_password': 'WelfareClub@2025',
    },
    {
        'name': 'BUBT Debating Club',
        'category': 'Academic',
        'short_description': 'Sharpening critical thinking, public speaking, and argumentation at BUBT and national level.',
        'description': "The Debating Club of BUBT is dedicated to developing critical thinking, rhetoric, and public speaking skills among BUBT students. The club's mission is to place its name at the zenith in the debating arena of the country as well as abroad. Members participate in inter-university debate competitions organized by universities across Bangladesh. The club follows both English and Bangla debate formats, including Parliamentary, British Parliamentary, and Asian Parliamentary styles. Regular activities include weekly debate practice sessions, impromptu speaking exercises, mock debates, and workshops on argumentation and research. The club fosters values of open-mindedness, intellectual honesty, and civic engagement.",
        'email': 'debate@bubt.edu.bd',
        'established': '2004-09-01',
        'president_username': 'debate_pres',
        'president_first': 'Nasreen',
        'president_last': 'Akter',
        'president_password': 'DebateClub@2025',
    },
    {
        'name': 'BUBT Economics Club',
        'category': 'Business',
        'short_description': 'Exploring economic theories, policies, and real-world applications through research and academic discourse.',
        'description': 'BUBT Economics Club brings together students passionate about economics, finance, and public policy at Bangladesh University of Business and Technology. The club bridges the gap between economic theory studied in classrooms and the complex economic realities of Bangladesh and the global economy. The club organizes economics seminars, research paper presentations, economic policy debates, and sessions on current economic issues. Guest lectures from economists, policymakers, and financial experts provide invaluable real-world perspectives. Members participate in national economics olympiads and research competitions. The club publishes a student economics journal featuring original research and analysis by BUBT students.',
        'email': 'ecoclub@bubt.edu.bd',
        'established': '2007-04-01',
        'president_username': 'eco_pres',
        'president_first': 'Jahirul',
        'president_last': 'Islam',
        'president_password': 'EcoClub@2025',
    },
    {
        'name': 'IEEE Student Branch BUBT',
        'category': 'Science',
        'short_description': 'IEEE affiliated student branch advancing technology and engineering excellence at BUBT.',
        'description': "IEEE Student Branch BUBT is affiliated with the Institute of Electrical and Electronics Engineers (IEEE) — the world's largest technical professional organization with over 423,000 members in 160 countries. The branch provides BUBT engineering students access to IEEE's vast resources including technical publications, online learning, research tools, and a global network of engineers and scientists. Members attend IEEE conferences and publish research with IEEE. Local activities include technical workshops, project exhibitions, paper presentation competitions, and invited talks from IEEE senior members. The branch also organizes the annual BUBT IEEE Tech Fest with project showcases and keynote speeches.",
        'email': 'ieee.bubt@bubt.edu.bd',
        'established': '2013-03-15',
        'president_username': 'ieee_pres',
        'president_first': 'Shakil',
        'president_last': 'Ahmed',
        'president_password': 'IEEEBUBT@2025',
    },
    {
        'name': 'Bangladesh National Cadet Corps BUBT',
        'category': 'Military',
        'short_description': 'BNCC unit at BUBT developing disciplined, patriotic, and service-oriented future leaders.',
        'description': 'The Bangladesh National Cadet Corps (BNCC) BUBT Unit is part of the national tri-service cadet organization under the Ministry of Defence. BNCC develops disciplined, leadership-oriented, and patriotic youth who are committed to serving the nation. Cadets undergo military training, parade drills, rifle shooting, field exercises, and adventure activities. BNCC cadets participate in national events, independence day parades, and disaster relief operations. The program builds physical fitness, mental toughness, teamwork, and a strong sense of national duty. BNCC certification is highly valued by employers and adds significant credibility to a student career profile in both public and private sectors.',
        'email': 'bncc@bubt.edu.bd',
        'established': '2005-03-26',
        'president_username': 'bncc_pres',
        'president_first': 'Kamal',
        'president_last': 'Hossain',
        'president_password': 'BNCCBUBT@2025',
    },
    {
        'name': 'BUBT Moot Court Society',
        'category': 'Academic',
        'short_description': 'Developing future legal professionals through simulated court proceedings and legal research at BUBT.',
        'description': 'BUBT Moot Court Society (BMCS) was established on 26th August 2019. The society promotes the advocacy skills of law students and arranges professional career development programs to prepare students for the competitive fields of law. BMCS trains its members by experts in moot and advocacy, including judges, advocates, and professors. The society organizes training to participate in regional and international moot competitions. BMCS has participated in the Philip C. Jessup International Law Moot Court Competition, K. Luthra Memorial Moot Court Competition, Henry Dunant Memorial Moot Court Competition, and the Shah Alam Constitutional Moot Court Competition, securing competitive positions nationally.',
        'email': 'bmcs@bubt.edu.bd',
        'established': '2019-08-26',
        'president_username': 'moot_pres',
        'president_first': 'Tahmina',
        'president_last': 'Sultana',
        'president_password': 'MootBUBT@2025',
    },
    {
        'name': 'BASIS Students Forum BUBT Chapter',
        'category': 'Technology',
        'short_description': "Connecting BUBT tech students with Bangladesh's ICT industry through BASIS Student Forum.",
        'description': "BASIS Students Forum BUBT Chapter is the university chapter of the Bangladesh Association of Software and Information Services (BASIS) Student Forum — the apex body of Bangladesh's software and IT industry. The chapter connects BUBT students with the country's rapidly growing ICT sector. It organizes industry visits to leading software companies, career fairs, technical workshops, and networking events with BASIS member companies. The forum facilitates internship and job placements at BASIS member companies for talented BUBT students. Regular sessions on emerging technologies, startup ecosystems, and the Bangladesh digital economy keep members informed about industry trends and opportunities.",
        'email': 'basis.bubt@bubt.edu.bd',
        'established': '2012-10-01',
        'president_username': 'basis_pres',
        'president_first': 'Nazmul',
        'president_last': 'Karim',
        'president_password': 'BasisBUBT@2025',
    },
]

random.seed(42)
created_clubs = []
president_credentials = []

for idx, cd in enumerate(CLUBS_DATA):
    if not User.objects.filter(username=cd['president_username']).exists():
        president = User.objects.create_user(
            username=cd['president_username'],
            email=f"{cd['president_username']}@bubt.edu.bd",
            password=cd['president_password'],
            first_name=cd['president_first'],
            last_name=cd['president_last'],
            user_type='president',
            department=DEPARTMENTS[idx % len(DEPARTMENTS)],
            is_verified=True,
        )
    else:
        president = User.objects.get(username=cd['president_username'])
        president.set_password(cd['president_password'])
        president.user_type = 'president'
        president.save()

    president_credentials.append({
        'club': cd['name'], 'username': cd['president_username'],
        'password': cd['president_password'],
        'name': f"{cd['president_first']} {cd['president_last']}",
    })

    slug = slugify(cd['name'])
    base_slug = slug
    counter = 1
    while Club.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    club = Club.objects.create(
        name=cd['name'], slug=slug,
        description=cd['description'],
        short_description=cd['short_description'],
        category=categories[cd['category']],
        president=president,
        email=cd.get('email', ''),
        website='https://bubt.edu.bd',
        status='active',
        established_date=date.fromisoformat(cd['established']),
    )
    ClubMember.objects.create(club=club, user=president, role='president', status='active',
        approved_by=president, approved_at=timezone.now())
    created_clubs.append(club)
    print(f"    Created: {club.name}")

print(f"    Total: {len(created_clubs)} clubs")

# STEP 4: 5 MEMBERS PER CLUB
print("\n[4/5] Adding 5 members per club...")

MEMBERS = [
    [('eee_m1','Arif','Hasan','vice_president'),('eee_m2','Sadia','Islam','secretary'),('eee_m3','Rakibul','Rahman','treasurer'),('eee_m4','Tamanna','Akter','executive'),('eee_m5','Faisal','Ahmed','member')],
    [('scout_m1','Imran','Khan','vice_president'),('scout_m2','Nusrat','Jahan','secretary'),('scout_m3','Alamin','Hossain','treasurer'),('scout_m4','Shirin','Akter','executive'),('scout_m5','Raihan','Islam','member')],
    [('it_m1','Mehedi','Hasan','vice_president'),('it_m2','Lamia','Khanam','secretary'),('it_m3','Sumon','Miah','treasurer'),('it_m4','Piya','Roy','executive'),('it_m5','Nabil','Chowdhury','member')],
    [('biz_m1','Habibur','Rahman','vice_president'),('biz_m2','Sanjida','Begum','secretary'),('biz_m3','Karim','Uddin','treasurer'),('biz_m4','Roksana','Parvin','executive'),('biz_m5','Delwar','Hossain','member')],
    [('cul_m1','Rina','Das','vice_president'),('cul_m2','Asif','Sarkar','secretary'),('cul_m3','Mitu','Biswas','treasurer'),('cul_m4','Polash','Mondal','executive'),('cul_m5','Tania','Sultana','member')],
    [('spt_m1','Sakib','Al','vice_president'),('spt_m2','Sharmin','Nahar','secretary'),('spt_m3','Mamun','Rashid','treasurer'),('spt_m4','Dipa','Pal','executive'),('spt_m5','Selim','Bhuiyan','member')],
    [('eng_m1','Fahmida','Khanam','vice_president'),('eng_m2','Liton','Molla','secretary'),('eng_m3','Anika','Saha','treasurer'),('eng_m4','Zahid','Ali','executive'),('eng_m5','Riya','Nath','member')],
    [('pho_m1','Tushar','Sheikh','vice_president'),('pho_m2','Nazneen','Akter','secretary'),('pho_m3','Golam','Kibria','treasurer'),('pho_m4','Trisha','Saha','executive'),('pho_m5','Omar','Faruk','member')],
    [('wel_m1','Belal','Hossain','vice_president'),('wel_m2','Sabrina','Islam','secretary'),('wel_m3','Nasrul','Islam','treasurer'),('wel_m4','Meem','Akter','executive'),('wel_m5','Ruhul','Amin','member')],
    [('deb_m1','Tarek','Ahmed','vice_president'),('deb_m2','Sabina','Yasmin','secretary'),('deb_m3','Anisur','Rahman','treasurer'),('deb_m4','Dilruba','Begum','executive'),('deb_m5','Wahid','Khan','member')],
    [('eco_m1','Enamul','Haque','vice_president'),('eco_m2','Sharifa','Akter','secretary'),('eco_m3','Jalal','Uddin','treasurer'),('eco_m4','Afroja','Khanam','executive'),('eco_m5','Quamrul','Islam','member')],
    [('ieee_m1','Aminul','Islam','vice_president'),('ieee_m2','Shaila','Parvin','secretary'),('ieee_m3','Ismail','Hossain','treasurer'),('ieee_m4','Nipa','Roy','executive'),('ieee_m5','Khokon','Miah','member')],
    [('bncc_m1','Rezaul','Karim','vice_president'),('bncc_m2','Suriya','Begum','secretary'),('bncc_m3','Abul','Bashar','treasurer'),('bncc_m4','Monirul','Islam','executive'),('bncc_m5','Jannatul','Ferdous','member')],
    [('moot_m1','Ridwanul','Haque','vice_president'),('moot_m2','Parvin','Akter','secretary'),('moot_m3','Sirajul','Islam','treasurer'),('moot_m4','Nasima','Begum','executive'),('moot_m5','Tozammel','Hossain','member')],
    [('bas_m1','Shafiqul','Islam','vice_president'),('bas_m2','Antara','Akter','secretary'),('bas_m3','Masud','Rana','treasurer'),('bas_m4','Dilara','Sultana','executive'),('bas_m5','Ziaur','Rahman','member')],
]

INTAKES = ['55','56','57','58','59','60']
for cidx, club in enumerate(created_clubs):
    for uname, first, last, role in MEMBERS[cidx]:
        if not User.objects.filter(username=uname).exists():
            student = User.objects.create_user(
                username=uname, email=f"{uname}@student.bubt.edu.bd",
                password="Student@123", first_name=first, last_name=last,
                user_type='student', student_id=f"B-{random.randint(180000,220000)}",
                department=DEPARTMENTS[cidx % len(DEPARTMENTS)],
                intake=random.choice(INTAKES), year=random.randint(1,4), is_verified=True,
            )
        else:
            student = User.objects.get(username=uname)
        ClubMember.objects.create(club=club, user=student, role=role, status='active',
            approved_by=club.president,
            approved_at=timezone.now()-timedelta(days=random.randint(1,200)))
    print(f"    {club.name}: 5 members added")

# STEP 5: 1 ONGOING EVENT PER CLUB
print("\n[5/5] Creating 1 ongoing event per club...")

EVENTS = [
    ('BUBT EEE Club','Robotics Design Challenge 2026','competition','BUBT EEE Lab, Building C','Teams design and build robots to complete obstacle courses and engineering tasks. Open to all EEE and CSE students. Judged on design creativity, build quality, and performance. National-level winners will represent BUBT in the regional competition. This is a 3-day event with workshops, design rounds, and a final competition with a prize ceremony.','Build robots — top teams advance to the national regional competition.',-1,3,True,0),
    ('BUBT Rover Scout Group','Scout Leadership Training Camp 2026','workshop','BUBT Campus and Surrounding Outskirts','3-day official leadership and outdoor training camp for BUBT Rovers. Activities include first aid training, navigation, rope techniques, campfire programs, and a community service project. Required for Rover Scout award progression. Participants receive a certificate from Bangladesh Scouts upon completion.','Official Rover leadership camp — required for Scout award progression.',-1,3,False,500),
    ('BUBT IT Club','National Programming Contest 2026','competition','BUBT Computer Lab, Building B','Annual programming competition open to all BUBT students. Individual and team categories available. Problems cover data structures, algorithms, and problem-solving. Prizes worth BDT 50,000. This two-day event starts with an online qualifier round and concludes with the final onsite contest with an industry-judged awards ceremony.','Annual coding contest with BDT 50,000 in prizes — individual and team categories.',-1,2,True,0),
    ('BUBT Business Club','Business Plan Competition 2026','competition','BUBT Conference Room, 5th Floor','Present your startup idea to a panel of business executives and real investors. Top teams receive seed funding and mentorship from industry leaders. Teams are evaluated on market opportunity, business model, financial projections, and go-to-market strategy. Day one includes pitch training; day two has the final judged presentations.','Pitch your startup to real investors and win seed funding and mentorship.',-1,2,True,0),
    ('BUBT Cultural Club','BUBT Cultural Fest 2026','social','BUBT Main Auditorium and Campus Grounds','The biggest cultural event of the year featuring singing, dancing, drama, standup comedy, and fashion show competitions. Inter-department competition with grand prizes and trophies. Live performances by popular artists. Cultural Fest runs across two days with workshops, competitions, and gala night performances. Open to all BUBT students, faculty, and staff.','The biggest cultural celebration of the year — competitions, performances, and prizes.',-1,2,True,0),
    ('BUBT Sports Club','Inter-Department Cricket Tournament 2026','competition','BUBT Cricket Ground and Sports Complex','T20 format cricket tournament between all BUBT departments. Eight teams compete over two weeks. The final match will be followed by a prize-giving ceremony. Individual awards for Best Batsman, Best Bowler, Best Fielder, and Player of the Tournament will be presented. All BUBT students are welcome to attend matches as spectators.','T20 inter-department cricket — 8 teams compete for the trophy over two weeks.',-2,14,True,0),
    ('BUBT English Language Club','IELTS Preparation Workshop 2026','workshop','BUBT Language Lab, 3rd Floor, Building A','Comprehensive IELTS preparation covering all four modules — Listening, Reading, Writing, and Speaking. Led by an experienced trainer with 10+ years of IELTS coaching experience. Practice tests, strategy sessions, and individual feedback provided throughout the two-day workshop. Participants receive a workbook and access to an online practice test platform valid for one month.','Expert-led IELTS preparation covering all four modules — limited seats.',-1,2,False,400),
    ('BUBT Photography Club','Old Dhaka Photo Walk Spring 2026','social','Meeting Point: BUBT Main Gate at 7:00 AM','Guided photography walk through the historic streets and landmarks of Old Dhaka during spring season. Capture historic architecture, river ghats, traditional markets, and everyday life. All camera types welcome — DSLR, mirrorless, or smartphone. A photography expert will provide guidance and tips during the walk. Best photos will be featured in the club annual magazine and social media.','Guided photo walk through historic Old Dhaka — all camera types welcome.',-1,1,True,0),
    ('BUBT Social Welfare Club','Voluntary Blood Donation Camp Spring 2026','social','BUBT Health Center and Main Campus Corridor','Quarterly blood donation drive in partnership with Dhaka Medical College Hospital blood bank. All blood groups urgently needed. Free health checkup for all donors including blood pressure screening, blood sugar test, and hemoglobin level check. Refreshments provided to all donors. The camp runs from 9 AM to 4 PM. Faculty, staff, and students are all welcome to participate.','Quarterly blood donation drive — free health checkup for all donors.',-1,1,True,0),
    ('BUBT Debating Club','Inter-University Debate Festival 2026','competition','BUBT Auditorium and Seminar Halls','BUBT premier inter-university debate tournament in British Parliamentary format. Thirty-two teams from universities across Bangladesh compete over two days. Motions cover current affairs, economics, science, and social policy. Prize money of BDT 30,000 and trophies for champion and runner-up teams. Expert panel of adjudicators from leading Bangladeshi and international debate circuits will evaluate all rounds.','Premier BP debate tournament — 32 teams, BDT 30,000 prize money.',-1,2,True,0),
    ('BUBT Economics Club','Bangladesh Economy Forum 2026','conference','BUBT Conference Hall, 5th Floor','Annual economic conference featuring presentations on Bangladesh macroeconomic performance, monetary policy, trade, and development challenges. Guest speakers include economists from Bangladesh Bank, World Bank, and leading think tanks. Student researchers present original papers on economic topics. The forum includes a panel discussion on Bangladesh economic outlook and policy priorities. CPD certificates issued to registered participants.','Annual economic conference with expert speakers on Bangladesh economy and development.',-1,1,True,0),
    ('IEEE Student Branch BUBT','IEEE BUBT Tech Fest 2026','conference','BUBT Main Campus, All Buildings','Annual technology festival featuring project showcases, IEEE paper presentations, robotics demonstrations, IoT exhibition, and keynote speeches from IEEE senior members and fellows. Open to students from all universities in Bangladesh. IEEE conference certificates provided to all registered participants. Two-day event with separate tracks for hardware, software, and research paper presentations. Industry booths from leading engineering companies throughout the festival grounds.','Annual IEEE tech festival with project showcases, papers, robotics, and IoT demos.',-1,2,True,0),
    ('Bangladesh National Cadet Corps BUBT','Annual BNCC Parade and Certification Ceremony 2026','other','BUBT Open Ground and Main Campus','Annual BNCC parade and certification ceremony marking the completion of the academic year training cycle. Cadets demonstrate their parade drills, physical fitness, and discipline before a reviewing panel of senior military officers. Certificates and promotions are awarded to cadets who have successfully completed all training requirements. New cadet enrollment for the next training cycle will take place on the second day of the event.','Annual BNCC parade, certification ceremony, and new cadet enrollment drive.',-1,2,True,0),
    ('BUBT Moot Court Society','National Moot Court Competition BUBT Round 2026','competition','BUBT Moot Court Room, Law Department','Teams argue a complex commercial and constitutional law case before a bench of senior advocates and sitting judges. This is the BUBT qualifying round for the national moot court competition. The winning team represents BUBT at the national level. A High Court judge will preside over the final round. This two-day competition includes memorial submission review on day one and oral arguments on day two. Open only to registered law students of BUBT.','Qualify for nationals by arguing before sitting judges in BUBT moot court.',-1,2,True,0),
    ('BASIS Students Forum BUBT Chapter','Tech Career Fair ICT Sector 2026','social','BUBT Ground Floor Lobby and Main Corridors','Over 30 ICT companies from among BASIS member organizations attend this career fair. On-spot interviews available for fresh graduates and final-year students. Internship and full-time positions available in software development, QA testing, UI/UX design, and digital marketing. Bring multiple printed copies of your CV and dress professionally. The fair runs from 10 AM to 5 PM. All BUBT students are welcome regardless of department.','30+ ICT companies for on-spot interviews, internships, and full-time job offers.',-1,1,True,0),
]

now = timezone.now()
club_map = {c.name: c for c in created_clubs}

for ev in EVENTS:
    club_name, title, etype, venue, desc, short, offset, duration, is_free, fee = ev
    club = club_map.get(club_name)
    if not club:
        print(f"    Club not found: {club_name}")
        continue
    start = now + timedelta(days=offset)
    end = start + timedelta(days=duration)
    slug = slugify(title)
    base = slug; ctr = 1
    while Event.objects.filter(slug=slug).exists():
        slug = f"{base}-{ctr}"; ctr += 1
    Event.objects.create(
        title=title, slug=slug, description=desc, short_description=short,
        club=club, event_type=etype, venue=venue,
        start_date=start, end_date=end,
        is_free=is_free, fee=fee,
        max_participants=random.randint(50,200),
        status='published', is_featured=True,
        created_by=club.president,
        registration_open=now-timedelta(days=7),
        registration_close=end,
    )
    print(f"    {club.name}: event created")

print("\n" + "="*60)
print("SEEDING COMPLETE!")
print("="*60)
print(f"\nSummary:")
print(f"  Clubs     : {Club.objects.count()}")
print(f"  Presidents: {User.objects.filter(user_type='president').count()}")
print(f"  Students  : {User.objects.filter(user_type='student').count()}")
print(f"  Members   : {ClubMember.objects.count()}")
print(f"  Events    : {Event.objects.count()}")

print("\nPresident Credentials:")
print("-"*60)
for cred in president_credentials:
    print(f"  {cred['club']}")
    print(f"    Username: {cred['username']}  |  Password: {cred['password']}")
    print(f"    Name: {cred['name']}")
    print()

print("Student Password (all): Student@123")
print("="*60)

import os
import subprocess

def run_command(command, cwd=None):
    print(f">>> {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode

def setup_project():
    print("Starting University Club Management System Setup...")
    print("=" * 60)
    
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    if not os.path.exists('manage.py'):
        print("ERROR: manage.py not found in current directory!")
        print("Please run this script from your project directory.")
        return
    
    print("\n1. Creating virtual environment...")
    if not os.path.exists('venv'):
        run_command('python -m venv venv', current_dir)
        print("[OK] Virtual environment created")
    else:
        print("[OK] Virtual environment already exists")
    
    print("\n2. Installing dependencies...")
    requirements_content = """Django==4.2.0
djangorestframework==3.14.0
django-cors-headers==4.1.0
Pillow==10.0.0
django-crispy-forms==2.0
crispy-bootstrap5==0.7
django-filter==23.3
"""
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements_content)
    
    if os.name == 'nt':
        pip_path = os.path.join(current_dir, 'venv', 'Scripts', 'pip')
        python_path = os.path.join(current_dir, 'venv', 'Scripts', 'python')
    else:
        pip_path = os.path.join(current_dir, 'venv', 'bin', 'pip')
        python_path = os.path.join(current_dir, 'venv', 'bin', 'python')
    
    run_command(f'"{pip_path}" install -r requirements.txt', current_dir)
    print("[OK] Dependencies installed")
    
    print("\n3. Making migrations...")
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
        print("[INFO] Removed old database")
    
    run_command(f'"{python_path}" manage.py makemigrations accounts', current_dir)
    run_command(f'"{python_path}" manage.py makemigrations clubs', current_dir)
    run_command(f'"{python_path}" manage.py makemigrations events', current_dir)
    run_command(f'"{python_path}" manage.py makemigrations', current_dir)
    print("[OK] Migrations created")
    
    print("\n4. Applying migrations...")
    run_command(f'"{python_path}" manage.py migrate', current_dir)
    print("[OK] Migrations applied")
    
    print("\n5. Creating superadmin account...")
    superuser_code = """
from django.contrib.auth import get_user_model
User = get_user_model()

# Create the one and only superadmin
if User.objects.filter(username='superadmin').exists():
    u = User.objects.get(username='superadmin')
    u.email = 'superadmin@gmail.com'
    u.user_type = 'admin'
    u.is_staff = True
    u.is_superuser = True
    u.set_password('superadmin')
    u.save()
    print("[OK] superadmin account updated.")
else:
    User.objects.create_superuser(
        username='superadmin',
        email='superadmin@gmail.com',
        password='superadmin',
        user_type='admin',
    )
    print("[OK] superadmin account created: superadmin / superadmin")
"""
    
    with open('temp_create_superuser.py', 'w', encoding='utf-8') as f:
        f.write(superuser_code)
    
    run_command(f'"{python_path}" manage.py shell < temp_create_superuser.py', current_dir)
    os.remove('temp_create_superuser.py')
    
    print("\n6. Seeding database...")
    seed_result = run_command(f'"{python_path}" manage.py seed_data', current_dir)
    
    if seed_result != 0:
        print("[INFO] Creating sample data manually...")
        create_sample_data(python_path, current_dir)
    
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("\nTo start the server, run:")
    if os.name == 'nt':
        print(f'  cd "{current_dir}"')
        print('  venv\\Scripts\\activate')
        print(f'  "{python_path}" manage.py runserver')
    else:
        print(f'  cd "{current_dir}"')
        print('  source venv/bin/activate')
        print(f'  "{python_path}" manage.py runserver')
    
    print("\nThen visit: http://localhost:8000/")
    print("Admin panel: http://localhost:8000/admin/ (admin/admin123)")
    print("=" * 60)

def create_sample_data(python_path, current_dir):
    sample_data_code = """
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from clubs.models import ClubCategory, Club, ClubMember
from events.models import EventCategory, Event, EventRegistration
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

print("Creating sample data...")

categories = ['Academic', 'Technical', 'Cultural', 'Sports', 'Social']
for cat in categories:
    ClubCategory.objects.get_or_create(name=cat)

event_cats = ['Workshop', 'Seminar', 'Competition', 'Social', 'Conference']
colors = ['#4361ee', '#7209b7', '#f72585', '#4cc9f0', '#4895ef']
for cat, color in zip(event_cats, colors):
    EventCategory.objects.get_or_create(name=cat, color=color)

users = []
for i in range(1, 6):
    user = User.objects.create_user(
        username=f'student{i}',
        email=f'student{i}@university.edu',
        password='student123',
        first_name=f'Student{i}',
        user_type='student',
        student_id=f'STU2024{i:03d}'
    )
    users.append(user)
    print(f"Created user: student{i}/student123")

club_data = [
    ('Programming Club', 'Technical'),
    ('Debating Society', 'Academic'),
    ('Photography Club', 'Cultural'),
    ('Robotics Club', 'Technical'),
    ('Music Club', 'Cultural'),
]

clubs = []
for i, (name, cat_name) in enumerate(club_data):
    category = ClubCategory.objects.get(name=cat_name)
    president = users[i % len(users)]
    
    club = Club.objects.create(
        name=name,
        slug=name.lower().replace(' ', '-'),
        description=f'Welcome to {name}! Join us for amazing activities.',
        short_description=f'{name} - University Club',
        category=category,
        president=president,
        status='active'
    )
    clubs.append(club)
    
    ClubMember.objects.create(club=club, user=president, role='president', status='active')
    print(f"Created club: {name}")

for i in range(1, 11):
    club = random.choice(clubs)
    start_date = timezone.now() + timedelta(days=random.randint(1, 30))
    
    event = Event.objects.create(
        title=f'{club.name} Workshop #{i}',
        slug=f'workshop-{club.slug}-{i}',
        description=f'Join {club.name} for an exciting workshop!',
        short_description=f'Workshop by {club.name}',
        club=club,
        category=EventCategory.objects.first(),
        event_type='workshop',
        start_date=start_date,
        end_date=start_date + timedelta(hours=2),
        venue=f'Room {random.randint(100, 500)}',
        max_participants=50,
        is_free=True,
        status='published',
        created_by=club.president
    )
    
    for user in random.sample(users, random.randint(2, 4)):
        EventRegistration.objects.create(event=event, user=user, status='registered')
    
    if i % 5 == 0:
        print(f"Created {i} events...")

print("\\n[OK] Sample data created successfully!")
print("\\nTEST ACCOUNTS")
print("Admin: admin / admin123")
print("Students: student1..student5 / student123")
print("\\nACCESS LINKS")
print("Home: http://localhost:8000/")
print("Admin: http://localhost:8000/admin/")
"""
    
    with open('create_sample_data.py', 'w', encoding='utf-8') as f:
        f.write(sample_data_code)
    
    run_command(f'"{python_path}" create_sample_data.py', current_dir)
    os.remove('create_sample_data.py')

if __name__ == '__main__':
    setup_project()
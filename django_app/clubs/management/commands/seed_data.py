from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed database with initial data'
    
    def handle(self, *args, **kwargs):
        self.stdout.write('Starting database seeding...')
        
        try:
            from clubs.models import ClubCategory, Club, ClubMember
            from events.models import EventCategory, Event, EventRegistration
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f'Error importing models: {e}'))
            return
        
        self.stdout.write('Creating superadmin account...')
        if not User.objects.filter(username='superadmin').exists():
            User.objects.create_superuser(
                username='superadmin',
                email='superadmin@gmail.com',
                password='superadmin',
                user_type='admin',
                is_staff=True,
                is_superuser=True,
            )
            self.stdout.write(self.style.SUCCESS('Superadmin created: superadmin / superadmin'))
        else:
            u = User.objects.get(username='superadmin')
            u.email = 'superadmin@gmail.com'
            u.user_type = 'admin'
            u.is_staff = True
            u.is_superuser = True
            u.save()
            self.stdout.write('Superadmin account already exists (updated).')

        self.stdout.write('Creating admin user...')
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@university.edu',
                password='admin123',
                first_name='Admin',
                last_name='User',
                user_type='admin'
            )
            self.stdout.write(self.style.SUCCESS('Admin user created: admin/admin123'))
        else:
            self.stdout.write('Admin user already exists')
        
        self.stdout.write('Creating club categories...')
        club_categories = [
            ('Academic', 'Academic and study-focused clubs', 'bi bi-book'),
            ('Technical', 'Technology and engineering clubs', 'bi bi-cpu'),
            ('Cultural', 'Arts and cultural clubs', 'bi bi-palette'),
            ('Sports', 'Sports and fitness clubs', 'bi bi-trophy'),
            ('Social', 'Social service and community clubs', 'bi bi-heart'),
        ]
        
        for name, desc, icon in club_categories:
            ClubCategory.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'icon': icon}
            )
        
        self.stdout.write('Creating event categories...')
        event_categories = [
            ('Workshop', 'bi bi-tools', '#4361ee'),
            ('Seminar', 'bi bi-mic', '#7209b7'),
            ('Competition', 'bi bi-trophy', '#f72585'),
            ('Social', 'bi bi-people', '#4cc9f0'),
            ('Conference', 'bi bi-building', '#4895ef'),
        ]
        
        for name, icon, color in event_categories:
            EventCategory.objects.get_or_create(
                name=name,
                defaults={'icon': icon, 'color': color}
            )
        
        self.stdout.write('Creating student users...')
        students = []
        student_data = [
            ('alice', 'Alice', 'Johnson', 'alice@university.edu', 'STU2024001', 'CSE'),
            ('bob', 'Bob', 'Smith', 'bob@university.edu', 'STU2024002', 'EEE'),
            ('charlie', 'Charlie', 'Brown', 'charlie@university.edu', 'STU2024003', 'BBA'),
            ('diana', 'Diana', 'Prince', 'diana@university.edu', 'STU2024004', 'MBA'),
            ('edward', 'Edward', 'Wilson', 'edward@university.edu', 'STU2024005', 'CIVIL'),
            ('fiona', 'Fiona', 'Miller', 'fiona@university.edu', 'STU2024006', 'ARCH'),
            ('george', 'George', 'Davis', 'george@university.edu', 'STU2024007', 'MECH'),
            ('hannah', 'Hannah', 'Taylor', 'hannah@university.edu', 'STU2024008', 'PHARM'),
        ]
        
        for username, first_name, last_name, email, student_id, dept in student_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'user_type': 'student',
                    'student_id': student_id,
                    'department': dept,
                }
            )
            if created:
                user.set_password('student123')
                user.save()
                students.append(user)
                self.stdout.write(f'   Created user: {username}/student123')
            else:
                students.append(user)
        
        self.stdout.write(f'Total students: {len(students)}')
        
        self.stdout.write('Creating clubs...')
        clubs_data = [
            ('Programming Club', 'Technical', 'Master programming and software development'),
            ('Robotics Club', 'Technical', 'Build robots and learn automation'),
            ('Debating Society', 'Academic', 'Improve public speaking and debate skills'),
            ('Photography Club', 'Cultural', 'Learn and practice photography'),
            ('Music Club', 'Cultural', 'Music performances and learning'),
            ('Sports Club', 'Sports', 'Various sports activities'),
            ('Volunteer Club', 'Social', 'Community service projects'),
            ('Business Club', 'Academic', 'Entrepreneurship and business skills'),
        ]
        
        clubs = []
        for i, (name, category_name, description) in enumerate(clubs_data):
            category = ClubCategory.objects.get(name=category_name)
            president = students[i % len(students)]
            
            club, created = Club.objects.get_or_create(
                name=name,
                defaults={
                    'slug': name.lower().replace(' ', '-'),
                    'description': description,
                    'short_description': description[:100] + '...',
                    'category': category,
                    'president': president,
                    'status': 'active',
                    'established_date': timezone.now().date() - timedelta(days=random.randint(100, 1000))
                }
            )
            clubs.append(club)
            
            ClubMember.objects.get_or_create(
                club=club,
                user=president,
                defaults={
                    'role': 'president',
                    'status': 'active'
                }
            )
            
            self.stdout.write(f'   Created club: {name}')
        
        self.stdout.write('Adding members to clubs...')
        for club in clubs:
            # Make sure we don't try to sample more students than available
            max_members = min(len(students) - 1, 8)  # -1 because president is already a member
            num_members = random.randint(3, max_members)
            
            # Get students who are not already president of this club
            available_students = [s for s in students if s != club.president]
            
            if available_students and num_members <= len(available_students):
                for user in random.sample(available_students, num_members):
                    if not ClubMember.objects.filter(club=club, user=user).exists():
                        role = random.choice(['member', 'executive', 'secretary', 'treasurer'])
                        ClubMember.objects.create(
                            club=club,
                            user=user,
                            role=role,
                            status='active'
                        )
        
        self.stdout.write('Creating events...')
        event_types = ['workshop', 'seminar', 'competition', 'social', 'meeting']
        
        for i in range(1, 11):
            club = random.choice(clubs)
            start_date = timezone.now() + timedelta(days=random.randint(1, 30))
            category = EventCategory.objects.first()
            event_type = random.choice(event_types)
            
            event = Event.objects.create(
                title=f'{club.name} {event_type.title()} #{i}',
                slug=f'{event_type}-{club.slug}-{i}',
                description=f'Join {club.name} for an exciting {event_type}. This event will feature expert speakers and hands-on activities.',
                short_description=f'A {event_type} by {club.name}',
                club=club,
                category=category,
                event_type=event_type,
                start_date=start_date,
                end_date=start_date + timedelta(hours=random.randint(2, 4)),
                venue=f'Room {random.randint(100, 500)}, Main Building',
                max_participants=random.choice([50, 100]),
                is_free=True,
                status='published',
                created_by=club.president
            )
            
            # Register random users for the event
            num_registrations = random.randint(5, min(15, len(students)))
            if num_registrations <= len(students):
                for user in random.sample(students, num_registrations):
                    EventRegistration.objects.get_or_create(
                        event=event,
                        user=user,
                        defaults={
                            'status': 'registered'
                        }
                    )
            
            if i % 5 == 0:
                self.stdout.write(f'   Created {i} events...')
        
        self.stdout.write(self.style.SUCCESS('\nDatabase seeding completed successfully!'))
        self.stdout.write('\n' + '='*50)
        self.stdout.write('TEST ACCOUNTS')
        self.stdout.write('='*50)
        self.stdout.write('Admin: admin / admin123')
        self.stdout.write('Students:')
        for student in ['alice', 'bob', 'charlie', 'diana', 'edward', 'fiona', 'george', 'hannah']:
            self.stdout.write(f'  {student} / student123')
        self.stdout.write('\nACCESS LINKS')
        self.stdout.write('Home: http://localhost:8000/')
        self.stdout.write('Admin: http://localhost:8000/admin/')
        self.stdout.write('Clubs: http://localhost:8000/clubs/')
        self.stdout.write('Events: http://localhost:8000/events/')
        self.stdout.write('='*50)
# -*- coding: utf-8 -*-
import csv
import datetime

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Time, Sequence
from sqlalchemy.orm import sessionmaker

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import exists


Base = declarative_base()


class Course(Base):
    __tablename__ = 'course'

    id = Column(Integer, Sequence('author_id_seq'), primary_key=True)
    name = Column(String)

    schoolchildren = relationship('Schoolchild', order_by='Schoolchild.id', back_populates='course')
    course_schedules = relationship('Schedule', order_by='Schedule.time_from', back_populates='course')

    def __repr__(self):
        return "{} {}".format(self.name)


class Schoolchild(Base):
    __tablename__ = 'schoolchild'

    id = Column(Integer, Sequence('author_id_seq'), primary_key=True)
    firstname = Column(String)
    lastname = Column(String)
    course_id = Column(Integer, ForeignKey('course.id'))

    course = relationship('Course', back_populates='schoolchildren')

    def __repr__(self):
        return "{} {}".format(self.firstname, self.lastname)


class Teacher(Base):
    __tablename__ = 'teacher'

    id = Column(Integer, Sequence('author_id_seq'), primary_key=True)
    firstname = Column(String)
    lastname = Column(String)

    teacher_schedules = relationship('Schedule', order_by='Schedule.time_from', back_populates='teacher')

    def __repr__(self):
        return "{} {}".format(self.firstname, self.lastname)


class Schedule(Base):
    __tablename__ = 'schedule'
    
    id = Column(Integer, Sequence('author_id_seq'), primary_key=True)
    # Weekday saved as ISO format
    # https://docs.python.org/3/library/datetime.html#datetime.date.isoweekday
    weekday = Column(Integer)
    time_from = Column(Time)
    time_to = Column(Time)
    course_id = Column(Integer, ForeignKey('course.id'))
    teacher_id = Column(Integer, ForeignKey('teacher.id'))

    course = relationship('Course', back_populates='course_schedules')
    teacher = relationship('Teacher', back_populates='teacher_schedules')

    def __repr__(self):
        return "{} {}".format(self.name)


class CourseReport(object):

    def __init__(self, path):
        self.path = path

    def export(self, course):
        schoolchildren = course.schoolchildren
        with open(self.path, 'w') as a_file:
            writer = csv.writer(a_file)
            for schoolchild in schoolchildren:
                writer.writerow([str(schoolchild)])


class CourseScheduleReport(object):

    def __init__(self, path):
        self.path = path

    def export(self, course):
        schedules = course.course_schedules
        with open(self.path, 'w') as a_file:
            writer = csv.writer(a_file)
            for schedule in schedules:
                writer.writerow([schedule.weekday, schedule.time_from, schedule.time_to, schedule.teacher])


class TeacherScheduleReport(object):
    
    def __init__(self, path):
        self.path = path

    def export(self, teacher):
        schedules = teacher.teacher_schedules
        with open(self.path, 'w') as a_file:
            writer = csv.writer(a_file)
            for schedule in schedules:
                writer.writerow([schedule.weekday, schedule.time_from, schedule.time_to, schedule.course.name])


def main(*args, **kwargs):
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    a_course = Course(name='1A')
    another_course = Course(name='1B')

    a_schoolchild = Schoolchild(firstname='Lucas', lastname='Renx', course=a_course)
    another_schoolchild = Schoolchild(firstname='Pedro', lastname='Gray', course=another_course)
    a_third_schoolchild = Schoolchild(firstname='Maria', lastname='Ferry', course=a_course)

    a_teacher = Teacher(firstname='Jorge', lastname='Manzano')

    a_time = datetime.time(8, 0, 0)
    another_time = datetime.time(10, 0, 0)
    a_third_time = datetime.time(12, 0, 0)

    a_schedule = Schedule(weekday=1, time_from=a_time, time_to=another_time, course=a_course, teacher=a_teacher)
    another_schedule = Schedule(weekday=1, time_from=another_time, time_to=a_third_time,
                                course=another_course, teacher=a_teacher)
    
    session.add(a_course)
    session.add(another_course)

    session.add(a_schoolchild)
    session.add(another_schoolchild)
    session.add(a_third_schoolchild)

    session.add(a_teacher)

    session.add(a_schedule)
    session.add(another_schedule)

    session.commit()

    CourseReport('course_{}.csv'.format(a_course.name)).export(a_course)
    CourseReport('course_{}.csv'.format(another_course.name)).export(another_course)

    CourseScheduleReport('course_schedule_{}.csv'.format(a_course.name)).export(a_course)
    CourseScheduleReport('course_schedule_{}.csv'.format(another_course.name)).export(another_course)

    TeacherScheduleReport('teacher_schedule_{}.csv'.format(a_teacher)).export(a_teacher)


if __name__ == "__main__":
    main()
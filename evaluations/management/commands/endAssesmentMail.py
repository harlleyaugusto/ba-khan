from datetime import date, timedelta
import json
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum,Count
from bakhanapp.models import Grade,Assesment,Assesment_Config,Assesment_Skill,Student_Skill,Skill_Progress,Skill,Video_Playing

class Command(BaseCommand):
    help = 'Envia un mail con la nota y las variables de empegno y desempegno'

    def handle(self, *args, **options):
        #funcion que se ejecutara al hacer python manage.py calculateGrade
        lastDate = date.today() - timedelta(days=1)
        #cambiar end_date__lgt
        assesments = Assesment.objects.filter(end_date__lte=lastDate).values('id_assesment_conf_id','id_assesment','name','start_date','end_date','grade__grade',
            'grade__kaid_student_id','grade__performance_points')#inner join django 1-N desde 1 hacia N
        #assesments = Assesment.objects.filter(end_date=lastDate)
        conf = 0 
        for assesment in assesments: #en assesment se encuantral las assesments y grades con kaid students
            if conf != assesment['id_assesment_conf_id']: #consulta las habilidaes cuando cambia assesment_config
                skills = getSelectedSkills(assesment['id_assesment_conf_id']) 
                conf = assesment['id_assesment_conf_id']
            video_time = getVideoTimeBetween(assesment['grade__kaid_student_id'],assesment['start_date'],assesment['end_date'])
            total_corrects = getSkillAttemptCorrect(assesment['id_assesment_conf_id'],assesment['grade__kaid_student_id'])
            total_incorrects = getSkillAttemptIncorrect(assesment['id_assesment_conf_id'],assesment['grade__kaid_student_id'])
            practiced,mastery1,mastery2,mastery3,struggling = getDomainLevel(assesment['id_assesment_conf_id'],assesment['grade__kaid_student_id'])
            #print 'tiempo en videos: %d, total correctas: %d total incorrectas: %d'%(video_time,total_corrects,total_incorrects)
            print practiced,mastery1,mastery2,mastery3,struggling

def getDomainLevel(id_assesment_config,kaid_student):
    practiced = Skill.objects.filter(assesment_skill__id_assesment_config_id=id_assesment_config,student_skill__kaid_student_id=kaid_student,student_skill__last_skill_progress='practiced').values(
        'student_skill__id_student_skill','student_skill__last_skill_progress').annotate(practiced=Count('student_skill__id_student_skill')).aggregate(Sum('practiced'))
    mastery1 = Skill.objects.filter(assesment_skill__id_assesment_config_id=id_assesment_config,student_skill__kaid_student_id=kaid_student,student_skill__last_skill_progress='mastery1').values(
        'student_skill__id_student_skill','student_skill__last_skill_progress').annotate(mastery1=Count('student_skill__id_student_skill')).aggregate(Sum('mastery1'))
    mastery2 = Skill.objects.filter(assesment_skill__id_assesment_config_id=id_assesment_config,student_skill__kaid_student_id=kaid_student,student_skill__last_skill_progress='mastery2').values(
        'student_skill__id_student_skill','student_skill__last_skill_progress').annotate(mastery2=Count('student_skill__id_student_skill')).aggregate(Sum('mastery2'))
    mastery3 = Skill.objects.filter(assesment_skill__id_assesment_config_id=id_assesment_config,student_skill__kaid_student_id=kaid_student,student_skill__last_skill_progress='mastery3').values(
        'student_skill__id_student_skill','student_skill__last_skill_progress').annotate(mastery3=Count('student_skill__id_student_skill')).aggregate(Sum('mastery3'))
    struggling = Skill.objects.filter(assesment_skill__id_assesment_config_id=id_assesment_config,student_skill__kaid_student_id=kaid_student,student_skill__struggling=True).values(
        'student_skill__id_student_skill','student_skill__last_skill_progress').annotate(struggling=Count('student_skill__id_student_skill')).aggregate(Sum('struggling'))
    if practiced['practiced__sum'] == None:
        practiced['practiced__sum'] = 0
    if mastery1['mastery1__sum'] == None:
        mastery1['mastery1__sum'] = 0
    if mastery2['mastery2__sum'] == None:
        mastery2['mastery2__sum'] = 0
    if mastery3['mastery3__sum'] == None:
        mastery3['mastery3__sum'] = 0
    if struggling['struggling__sum'] == None:
        struggling['struggling__sum'] = 0
    return practiced['practiced__sum'], mastery1['mastery1__sum'], mastery2['mastery2__sum'], mastery3['mastery3__sum'], struggling['struggling__sum']


def getSkillAttemptIncorrect(id_assesment_config,kaid_student):
    skills = Skill.objects.filter(assesment_skill__id_assesment_config_id=id_assesment_config,skill_attempt__kaid_student_id=kaid_student,skill_attempt__correct=False,skill_attempt__skipped=False).values('name_spanish',
        'skill_attempt__correct').annotate(incorrects = Count('skill_attempt__correct')).aggregate(Sum('incorrects'))
    #print 'respuesta de una consulta'
    if skills['incorrects__sum'] == None:
        incorrects = 0
    else:
        incorrects = skills['incorrects__sum']
    return incorrects

def getSkillAttemptCorrect(id_assesment_config,kaid_student):
    skills = Skill.objects.filter(assesment_skill__id_assesment_config_id=id_assesment_config,skill_attempt__kaid_student_id=kaid_student,skill_attempt__correct=True).values('name_spanish',
        'skill_attempt__correct').annotate(corrects = Count('skill_attempt__correct')).aggregate(Sum('corrects'))
    #print 'respuesta de una consulta'
    if skills['corrects__sum'] == None:
        corrects = 0
    else:
        corrects = skills['corrects__sum']
    return corrects

def getSelectedSkills(id_assesment_config):
    skills = Skill.objects.filter(assesment_skill__id_assesment_config_id=id_assesment_config).values('name_spanish','assesment_skill__id_assesment_config_id')
    return skills

def getVideoTimeBetween(kaid_s,t_begin,t_end):
    #Esta funcion entrega el tiempo que un estudiante ha utilizado en videos en un rango de fechas.
    query_set = Video_Playing.objects.filter(kaid_student=kaid_s,date__gte = t_begin,date__lte = t_end).aggregate(Sum('seconds_watched'))
    if query_set['seconds_watched__sum'] == None:
        return 0
    else:
        return query_set['seconds_watched__sum']
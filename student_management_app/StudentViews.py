import datetime
from django.shortcuts import redirect, render
from .models import file
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render

from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.urls import reverse

from .forms import DocumentForm

from student_management_app.models import Companies, Students, Courses, Subjects, CustomUser, Attendance, AttendanceReport, \
    LeaveReportStudent, FeedBackStudent, NotificationStudent, OnlineClassRoom, SessionYearModel


def student_home(request):
    student_obj=Students.objects.get(admin=request.user.id)
    attendance_total=Companies.objects.filter(student_id=student_obj).count()
    attendance_present=file.objects.filter(student_id=student_obj,leave_status=False).count()
    attendance_absent=file.objects.filter(student_id=student_obj,leave_status=True).count()
    course=Courses.objects.get(id=student_obj.course_id.id)
    subjects=file.objects.filter(student_id=student_obj).count()
    subjects_data=Subjects.objects.filter(course_id=course)
    session_obj=SessionYearModel.object.get(id=student_obj.session_year_id.id)
    class_room=OnlineClassRoom.objects.filter(subject__in=subjects_data,is_active=True,session_years=session_obj)

    subject_name=[]
    data_present=[]
    data_absent=[]
    subject_data=Subjects.objects.filter(course_id=student_obj.course_id)
    for subject in subject_data:
        attendance=Attendance.objects.filter(subject_id=subject.id)
        attendance_present_count=file.objects.filter(student_id=student_obj.id).count()
        attendance_absent_count=file.objects.filter(student_id=student_obj.id,leave_status=False,).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)
    attendance_present_count=file.objects.filter(student_id=student_obj.id).count()
    attendance_absent_count=file.objects.filter(student_id=student_obj.id,leave_status=True,).count()
    data_present.append(attendance_present_count)
    data_absent.append(attendance_absent_count)


    return render(request,"student_template/student_home_template.html",{"total_attendance":attendance_total,"attendance_absent":attendance_absent,"attendance_present":attendance_present,"subjects":subjects,"data_name":subject_name,"data1":data_present,"data2":data_absent,"class_room":class_room})

def join_class_room(request,subject_id,session_year_id):
    session_year_obj=SessionYearModel.object.get(id=session_year_id)
    subjects=Subjects.objects.filter(id=subject_id)
    if subjects.exists():
        session=SessionYearModel.object.filter(id=session_year_obj.id)
        if session.exists():
            subject_obj=Subjects.objects.get(id=subject_id)
            course=Courses.objects.get(id=subject_obj.course_id.id)
            check_course=Students.objects.filter(admin=request.user.id,course_id=course.id)
            if check_course.exists():
                session_check=Students.objects.filter(admin=request.user.id,session_year_id=session_year_obj.id)
                if session_check.exists():
                    onlineclass=OnlineClassRoom.objects.get(session_years=session_year_id,subject=subject_id)
                    return render(request,"student_template/join_class_room_start.html",{"username":request.user.username,"password":onlineclass.room_pwd,"roomid":onlineclass.room_name})

                else:
                    return HttpResponse("This Online Session is Not For You")
            else:
                return HttpResponse("This Subject is Not For You")
        else:
            return HttpResponse("Session Year Not Found")
    else:
        return HttpResponse("Subject Not Found")


def student_view_attendance(request):
    student=Students.objects.get(admin=request.user.id)
#    course=student.course_id
    subjects=Companies.objects.filter(student_id=student)
    return render(request,"student_template/student_view_attendance.html",{"subjects":subjects})

def student_view_attendance_post(request):
    #subject_id=request.POST.get("companies")
    
    
   # start_date=request.POST.get("start_date")
   # end_date=request.POST.get("end_date")

    #start_data_parse=datetime.datetime.strptime(start_date,"%Y-%m-%d").date()
    #end_data_parse=datetime.datetime.strptime(end_date,"%Y-%m-%d").date()
    #subject_obj=Companies.objects.get(id=1)
   # user_object=CustomUser.objects.get(id=request.user.id)
  #  stud_obj=Students.objects.get(admin=user_object)
 #   myfile = request.FILES['docfile']
    #fs = FileSystemStorage()
   # filename = fs.save(myfile.name, myfile)
  #  uploaded_file_url = fs.url(filename)


   # attendance=Attendance.objects.filter(attendance_date__range=(start_data_parse,end_data_parse),subject_id=subject_obj)
   # attendance_reports=AttendanceReport.objects.filter(attendance_id__in=attendance,student_id=stud_obj)
 #   newdoc = file(docfile=uploaded_file_url,student_id=stud_obj,companies_id=subject_obj)
#    newdoc.save()

            # Redirect to the document list after POST
   
    
    
    
     if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            user_object=CustomUser.objects.get(id=request.user.id)
            stud_obj=Students.objects.get(admin=user_object)
            subject_obj=Companies.objects.get(id=1)
            newdoc = file(docfile = request.FILES['docfile'],student_id=stud_obj,companies_id=subject_obj,leave_status=0)
            newdoc.save()
            messages.success(request, "Successfully Applied for Leave")
            return HttpResponseRedirect(reverse("student_view_attendance"))

            # Redirect to the document list after POST
     else:
        form = DocumentForm() # A empty, unbound form
        messages.error(request, "Failed To Apply for Leave")
        return HttpResponseRedirect(reverse("student_view_attendance"))

    # Load documents for the list page
    

    
     
def student_apply_leave(request):
    staff_obj = Students.objects.get(admin=request.user.id)
    leave_data=file.objects.filter(student_id=staff_obj).order_by("id").reverse()
    return render(request,"student_template/student_apply_leave.html",{"leave_data":leave_data})

def student_apply_leave_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_apply_leave"))
    else:
        leave_date=request.POST.get("leave_date")
        leave_msg=request.POST.get("leave_msg")

        student_obj=Students.objects.get(admin=request.user.id)
        try:
            leave_report=LeaveReportStudent(student_id=student_obj,leave_date=leave_date,leave_message=leave_msg,leave_status=0)
            leave_report.save()
            messages.success(request, "Successfully Applied for Leave")
            return HttpResponseRedirect(reverse("student_apply_leave"))
        except:
            messages.error(request, "Failed To Apply for Leave")
            return HttpResponseRedirect(reverse("student_apply_leave"))


def student_feedback(request):
    staff_id=Students.objects.get(admin=request.user.id)
    feedback_data=FeedBackStudent.objects.filter(student_id=staff_id)
    return render(request,"student_template/student_feedback.html",{"feedback_data":feedback_data})

def student_feedback_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_feedback"))
    else:
        feedback_msg=request.POST.get("feedback_msg")

        student_obj=Students.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackStudent(student_id=student_obj,feedback=feedback_msg,feedback_reply="")
            feedback.save()
            messages.success(request, "Successfully Sent Feedback")
            return HttpResponseRedirect(reverse("student_feedback"))
        except:
            messages.error(request, "Failed To Send Feedback")
            return HttpResponseRedirect(reverse("student_feedback"))

def student_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    student=Students.objects.get(admin=user)
    return render(request,"student_template/student_profile.html",{"user":user,"student":student})

def student_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        password=request.POST.get("password")
        address=request.POST.get("address")
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name
            if password!=None and password!="":
                customuser.set_password(password)
            customuser.save()

            student=Students.objects.get(admin=customuser)
            student.address=address
            student.save()
            messages.success(request, "Successfully Updated Profile")
            return HttpResponseRedirect(reverse("student_profile"))
        except:
            messages.error(request, "Failed to Update Profile")
            return HttpResponseRedirect(reverse("student_profile"))

@csrf_exempt
def student_fcmtoken_save(request):
    token=request.POST.get("token")
    try:
        student=Students.objects.get(admin=request.user.id)
        student.fcm_token=token
        student.save()
        return HttpResponse("True")
    except:
        return HttpResponse("False")

def student_all_notification(request):
    student=Students.objects.get(admin=request.user.id)
    notifications=NotificationStudent.objects.filter(student_id=student.id)
    return render(request,"student_template/all_notification.html",{"notifications":notifications})




def student_Companies(request):
    staff_id=Students.objects.get(admin=request.user.id)
    Companies_data=Companies.objects.filter(student_id=staff_id)
    return render(request,"student_template/student_Companies.html",{"Companies_data":Companies_data})

def student_Companies_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("student_Companies"))
    else:
        Companies_msg=request.POST.get("Companies_msg")
        student_obj=Students.objects.get(admin=request.user.id)
        try:
            companies=Companies(company_name=Companies_msg,student_id=student_obj)
            companies.save()
            messages.success(request, "Company successfully saved")
            return HttpResponseRedirect(reverse("student_Companies"))
        except:
            messages.error(request, "Failed To save company")
            return HttpResponseRedirect(reverse("student_Companies"))


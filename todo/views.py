from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TodoForm
from .models import Todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required


def home(request):
    return render(request, 'todo/index.html')

def signupuser(request):
    data = { 'form': UserCreationForm() }
    if request.method == 'GET':
        return render(request, 'todo/signup_user.html', data)
    else:
        # Greate a new user
        if request.POST['password1'] == request.POST['password2']:
            # Compare the password and confirm-password fields are the same.
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                data['error'] = 'That username is Taken. Please choose a new username.'
                return render(request, 'todo/signup_user.html', data)

        else:
            data['error'] = 'Passwords must match!'
            return render(request, 'todo/signup_user.html', data)

@login_required
def currenttodos(request):
    todos = Todo.objects.filter(user=request.user, date_completed__isnull=True)
    data = { 'todos': todos }
    return render(request, 'todo/current_todos.html', data)

@login_required
def completedtodos(request):
    todos = Todo.objects.filter(user=request.user, date_completed__isnull=False).order_by('-date_completed')
    data = { 'todos': todos }
    return render(request, 'todo/completed_todos.html', data)

def loginuser(request):
    data = { 'form': AuthenticationForm() }
    if request.method == 'GET':
        return render(request, 'todo/login.html', data)
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            data['error'] = 'Username and Password did not much'
            return render(request, 'todo/login.html', data)
        login(request, user)
        return redirect('currenttodos')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        data = { 'form': AuthenticationForm() }
        logout(request)
        return redirect('home')

@login_required
def createtodos(request):
    data = { 'form': TodoForm }
    if request.method == 'GET':
        return render(request, 'todo/create_todos.html', data)
    else:
        try:
            form = TodoForm(request.POST)
            new_todo = form.save(commit=False)
            new_todo.user = request.user
            new_todo.save()
            return redirect('currenttodos')
        except ValueError:
            data['error'] = 'Bad data passed in. Try Again.'
            return render(request, 'todo/create_todos.html', data)

@login_required
def todoitem(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    data = { 'todo': todo }
    if request.method == 'GET':
        data['form'] = TodoForm(instance=todo)
        return render(request, 'todo/todo_item.html', data)
    else:
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            data['form'] = form
            return redirect('currenttodos')
        except ValueError: 
            data['error'] = 'Bad Info'
            return render(request, 'todo/todo_item.html', data)

@login_required
def todocomplete(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    data = { 'todo': todo }
    if request.method == 'POST':
        todo.date_completed = timezone.now()
        todo.save()
        return redirect('currenttodos')

@login_required
def tododelete(request, todo_pk):
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)
    data = { 'todo': todo }
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')

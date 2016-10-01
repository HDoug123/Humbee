from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from .forms import GroupingForm
from .solve import solve

# Create your views here.

def index(request):
	context = { 'path': request.path }
	if request.method == 'POST':
		form = GroupingForm(request.POST)
		if form.is_valid():
			problem = form.cleaned_data['problem']
			groups, out = solve(problem, '/tmp/opa1')
			context['groups'] = groups
			context['output'] = out
			#return HttpResponseRedirect(reverse('grouping:result'))
	else:
		form = GroupingForm()
	context['form'] = form
	return render(request, 'main.html', context)

def result(request):
	context = {}
	return render(request, 'result.html', context)

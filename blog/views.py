from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse

from blog.models import BlogPost
from blog.forms import CreateBlogPostForm, UpdateBlogPostForm
from account.models import Account




def create_blog_view(request):

	context = {}

	user = request.user
	if not user.is_authenticated:
		return redirect('must_authenticate')

	form = CreateBlogPostForm(request.POST or None, request.FILES or None)
	if form.is_valid():
		obj = form.save(commit=False)
		author = Account.objects.filter(email=user.email).first()
		obj.author = author
		obj.save()
		form = CreateBlogPostForm()

	context['form'] = form

	return render(request, "blog/create_blog.html", context)


def detail_blog_view(request, slug):

	context = {}

	blog_post = get_object_or_404(BlogPost, slug=slug)
	context['blog_post'] = blog_post

	return render(request, 'blog/detail_blog.html', context)



def edit_blog_view(request, slug):

	context = {}

	user = request.user
	if not user.is_authenticated:
		return redirect("must_authenticate")

	blog_post = get_object_or_404(BlogPost, slug=slug)

	if blog_post.author != user:
		return HttpResponse('You are not the author of that post.')

	if request.POST:
		form = UpdateBlogPostForm(request.POST or None, request.FILES or None, instance=blog_post)
		if form.is_valid():
			obj = form.save(commit=False)
			obj.save()
			context['success_message'] = "Updated"
			blog_post = obj

	form = UpdateBlogPostForm(
			initial = {
					"title": blog_post.title,
					"body": blog_post.body,
					"image": blog_post.image,
			}
		)

	context['form'] = form
	return render(request, 'blog/edit_blog.html', context)


def get_blog_queryset(query=None):
	queryset = []
	queries = query.split(" ") # python install 2019 = [python, install, 2019]
	for q in queries:
		posts = BlogPost.objects.filter(
				Q(title__icontains=q) | 
				Q(body__icontains=q)
			).distinct()

		for post in posts:
			queryset.append(post)

	return list(set(queryset))

from .models import BlogPost, Comment
from .forms import  CommentForm

def post_detail(request, year, month, day, post):
    post = get_object_or_404(BlogPost, slug=post,
                                   status='published',
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day)

    # List of active comments for this post
    comments = post.comments.filter(active=True)

    new_comment = None

    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet          
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()                   
    return render(request,
                  'blog/detail_blog.html',
                  {'post': post,
                   'comments': comments,
                   'new_comment': new_comment,
                   'comment_form': comment_form})
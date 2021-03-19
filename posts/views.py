from django.http import JsonResponse
from django.db.models import Count, Q
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import CommentForm, PostForm
from .models import Post, Author, PostView
from marketing.forms import EmailSignupForm
from marketing.models import Signup
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.template.defaultfilters import slugify
from django.core.mail import send_mail
from django.conf import settings


form = EmailSignupForm()


def get_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None

def get_category_count():
    queryset = Post \
        .objects \
        .values('categories__title') \
        .annotate(Count('categories__title'))
    return queryset

def get_tags_count():
    queryset = Post \
        .objects \
        .values('tags__title') \
        .annotate(Count('tags__title'))
    return queryset


class SearchView(View):
    def get(self, request, *args, **kwargs):
        queryset = Post.objects.all()
        query = request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(overview__icontains=query)
            ).distinct()
        context = {
            'queryset': queryset
        }
        return render(request, 'search_results.html', context)


def blog_category(request, category):
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post_list = Post.objects.filter(
        categories__title=category
    )
    tags = get_tags_count()
    paginator = Paginator(post_list, 4)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'queryset': paginated_queryset,
        'most_recent': most_recent,
        'page_request_var': page_request_var,
        'category_count': category_count,
        'tags': tags,
        'form': form
    }
    return render(request, 'blog.html', context)


def ContactView(request):
    message_email = ""
    if request.method == 'POST':
        message_email = request.POST['email'] 
        message_subject  = request.POST['subject'] 
        message  = request.POST['message']
        #send a email
        send_mail(message_subject, message, settings.EMAIL_HOST_USER, [message_email])

    return render(request, "contacts.html", {'msg': message_email})


def blog_tags(request, tags):
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post_list = Post.objects.filter(
        tags__title=tags
    )
    tags = get_tags_count()
    paginator = Paginator(post_list, 4)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'queryset': paginated_queryset,
        'most_recent': most_recent,
        'page_request_var': page_request_var,
        'category_count': category_count,
        'tags': tags,
        'form': form
    }
    return render(request, 'blog.html', context)






class IndexView(View):
    form = EmailSignupForm()

    def get(self, request, *args, **kwargs):
        category_count = get_category_count()
        most_recent = Post.objects.filter(featured=True).order_by('-timestamp')[:3]
        post_list = Post.objects.filter(featured=True).all()
        tags = get_tags_count()
        paginator = Paginator(post_list, 5)
        page_request_var = 'page'
        page = request.GET.get(page_request_var)
        try:
            paginated_queryset = paginator.page(page)
        except PageNotAnInteger:
            paginated_queryset = paginator.page(1)
        except EmptyPage:
            paginated_queryset = paginator.page(paginator.num_pages)
        context = {
            'object_list': paginated_queryset,
            'most_recent': most_recent, 
            'page_request_var': page_request_var,
            'category_count': category_count,
            'tags': tags,
            'form': self.form
        }
        return render(request, 'index.html', context)

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        new_signup = Signup()
        new_signup.email = email
        new_signup.save()
        messages.info(request, "Successfully subscribed")
        return redirect("home")





class PostListView(ListView):
    form = EmailSignupForm()
    model = Post
    template_name = 'blog.html'
    context_object_name = 'queryset'
    paginate_by = 3

    def get_context_data(self, **kwargs):
        category_count = get_category_count()
        most_recent = Post.objects.order_by('-timestamp')[:3]
        tags = get_tags_count()
        context = super().get_context_data(**kwargs)
        context['most_recent'] = most_recent
        context['page_request_var'] = "page"
        context['category_count'] = category_count
        context['tags'] = tags
        context['form'] = self.form
        return context



class PostDetailView(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'
    form = CommentForm()

    def get_object(self):
        obj = super().get_object()
        if self.request.user.is_authenticated:
            PostView.objects.get_or_create(
                user=self.request.user,
                post=obj
            )
        return obj

    def get_context_data(self, **kwargs):
        category_count = get_category_count()
        vote_count = get_object_or_404(Post, id= self.kwargs['pk'])
        tags = get_object_or_404(Post, id= self.kwargs['pk'])
        rhs_tags = get_tags_count()
        most_recent = Post.objects.order_by('-timestamp')[:3]
        liked = False
        if vote_count.votes.filter(id = self.request.user.id).exists():
            liked = True

        context = super().get_context_data(**kwargs)
        context['most_recent'] = most_recent
        context['page_request_var'] = "page"
        context['category_count'] = category_count
        context['liked'] = liked
        context['vote_count'] = vote_count.vote_count
        context['tags'] = tags.get_tags[0],
        context['rhs_tags'] = rhs_tags[0],
        
        context['form'] = self.form
        return context

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            post = self.get_object()
            form.instance.user = request.user
            form.instance.post = post
            form.save()
            return redirect(reverse("post-detail", kwargs={
                'pk': post.pk   
            }))



class PostCreateView(CreateView):
    model = Post
    template_name = 'post_create.html'
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create'
        return context

    def form_valid(self, form):
        form.instance.author = get_author(self.request.user)
        form.save()
        return redirect(reverse("post-detail", kwargs={
            'pk': form.instance.pk,
            'slug': slugify(form.instance.title)
        }))




class PostUpdateView(UpdateView):
    model = Post
    template_name = 'post_create.html'
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update'
        return context

    def form_valid(self, form):
        form.instance.author = get_author(self.request.user)
        form.save()
        return redirect(reverse("post-detail", kwargs={
            'pk': form.instance.pk,
            'slug': slugify(form.instance.title)
        }))

def VoteView(request):
    iddy = request.POST.get('post_id')
    if request.method == 'POST':
        post = get_object_or_404(Post, id= iddy)
        liked = False
        if post.votes.filter(id = request.user.id).exists():
            post.votes.remove(request.user)
            liked = False
        else:
            post.votes.add(request.user)
            liked = True
    return JsonResponse({"data": liked}, status=200)


class PostDeleteView(DeleteView):
    model = Post
    success_url = '/blog'
    template_name = 'post_confirm_delete.html'


def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect(reverse("post-list"))

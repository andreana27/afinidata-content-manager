from django.urls import path, include
from posts import views
from rest_framework import routers


app_name = 'posts'

api_router = routers.DefaultRouter()
api_router.register(r'tip', views.TipsViewSet)

urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('new/', views.NewPostView.as_view(), name='new'),
    path('set_taxonomy', views.set_taxonomy, name='set-taxonomy'),
    path('<int:id>/edit/', views.EditPostView.as_view(), name="edit-post"),
    path('<int:id>/add_taxonomy/', views.AddTaxonomyView.as_view(), name="add_taxonomy"),
    path('<int:id>/', views.fetch_post, name="post"),
    path('<int:id>/delete/', views.DeletePostView.as_view(), name='delete'),
    path('<int:id>/send_to_review/', views.ChangePostStatusToReviewView.as_view(), name='send_to_review'),
    path('set_interaction/', views.set_interaction, name='set_interaction'),
    path('<int:id>/thumbnail/', views.get_thumbnail_by_post, name='get_thumbnail'),
    path('<int:pid>/review/', views.ReviewPostView.as_view(), name='review'),
    path('<int:id>/review/<int:review_id>/', views.ReviewView.as_view(), name='post-review'),
    path('<int:id>/review/<int:review_id>/add_comment/', views.AddReviewCommentView.as_view(), name='comment_review'),
    path('<int:review_id>/accept/', views.AcceptReviewView.as_view(), name='accept-review'),
    path('<int:review_id>/reject/', views.RejectionView.as_view(), name='reject-review'),
    path('<int:review_id>/request_changes/', views.ChangePostToNeedChangesView.as_view(), name='request_changes_view'),
    path('interaction/<int:id>/edit/', views.edit_interaction, name="interaction-edit"),
    path('feedback/', views.feedback, name="feedback"),
    path('<int:id>/statistics/', views.StatisticsView.as_view(), name='post-statistics'),
    path('<int:id>/activity/', views.post_activity, name='post-activity'),
    path('tags/create', views.create_tag, name="create-tag"),
    path('tags/', views.tags, name='tags'),
    path('<int:id>/set_tag', views.set_tag_to_post, name="set-tag-to-post"),
    path('<int:id>/get_tags', views.get_tags_for_post, name="get-tags-for-post"),
    path('<int:id>/remove_tag', views.remove_tag_for_post, name='remove-tag-for-post'),
    path('list/', views.PostsListView.as_view(), name="posts-list"),
    path('questions/<int:id>/', views.QuestionView.as_view(), name='question'),
    path('questions/', views.QuestionsView.as_view(), name='questions'),
    path('questions/new/', views.CreateQuestion.as_view(), name='new-question'),
    path('questions/<int:id>/edit/', views.EditQuestion.as_view(), name='edit-question'),
    path('questions/<int:id>/delete/', views.DeleteQuestionView.as_view(), name='delete-question'),
    path('<int:id>/questions/', views.question_by_post, name='question_by_post'),
    path('questions/<int:id>/response/', views.create_response_for_question, name='response-for-question'),
    path('questions/<int:id>/responses/new/', views.CreateQuestionResponseView.as_view(),
         name='create-question-response'),
    path('questions/<int:question_id>/responses/<int:response_id>/edit/', views.EditQuestionResponseView.as_view(),
         name='edit-response-for-question'),
    path('questions/<int:question_id>/responses/<int:response_id>/delete/', views.DeleteQuestionResponseView.as_view(),
         name='delete-response-for-question'),
    path('questions/<int:id>/replies/', views.get_replies_to_question, name='replies-for-question'),
    path('reviews/', views.Reviews.as_view(), name='reviews'),
    path('getPostForUser', views.get_posts_for_user, name='get-post-for-user'),
    path('getRecommendedPostForUser', views.getting_posts_reco, name='get-reco-post-for-user'),
    path('post_comment/', views.AddCommentToPostByUserView.as_view(), name="post_comment"),
    path('api/', include(api_router.urls)),
    path('set_complexity/', views.PostComplexityCreateApiView.as_view(), name="post_complexity"),
    path('get_post_by_area/', views.PostByArea.as_view(), name="post_by_area")
]

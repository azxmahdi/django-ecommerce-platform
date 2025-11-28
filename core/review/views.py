import logging

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.db import transaction

from common.mixins import CustomLoginRequiredMixin
from .forms import ProductCommentForm
from .models import ProductCommentModel
from core.constants import TaskName, LoggerName

apps_logger = logging.getLogger(LoggerName.APPS)


class ProductCommentCreateView(CustomLoginRequiredMixin, CreateView):
    http_method_names = ["post"]
    model = ProductCommentModel
    form_class = ProductCommentForm

    def get_form_kwargs(self):
        """پاس دادن request به فرم"""
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()

        product = form.cleaned_data["product"]
        apps_logger.info(
            "Product comment submitted successfully",
            extra={
                "task_name": TaskName.PRODUCT_COMMENT_SUBMIT,
                "user_id": self.request.user.id,
                "product_id": product.id,
                "comment_id": form.instance.id,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )
        messages.success(
            self.request,
            "دیدگاه شما با موفقیت ثبت شد و پس از بررسی نمایش داده خواهد شد",
        )
        return redirect(
            reverse_lazy("shop:product-detail", kwargs={"slug": product.slug})
        )

    def form_invalid(self, form):
        apps_logger.error(
            "Product comment submission failed",
            extra={
                "task_name": TaskName.PRODUCT_COMMENT_SUBMIT,
                "user_id": self.request.user.id,
                "errors": form.errors,
                "correlation_id": getattr(
                    self.request, "correlation_id", None
                ),
            },
        )
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return redirect(self.request.META.get("HTTP_REFERER"))

    def get_queryset(self):
        return ProductCommentModel.objects.filter(user=self.request.user)


class LikeOrDislikeProductCommentView(View):

    def post(self, request, *args, **kwargs):
        comment_id = request.POST.get("comment_id")
        action = request.POST.get("action")

        if not comment_id or action not in ["like", "dislike"]:
            apps_logger.error(
                "Invalid vote request",
                extra={
                    "task_name": TaskName.PRODUCT_COMMENT_VOTE_ERROR,
                    "user_id": request.user.id,
                    "comment_id": comment_id,
                    "action": action,
                    "correlation_id": getattr(request, "correlation_id", None),
                },
            )
            return JsonResponse(
                {"status": "error", "message": "داده‌ها ناقص است."}, status=400
            )

        try:
            with transaction.atomic():
                comment = ProductCommentModel.objects.select_for_update().get(
                    id=comment_id
                )

                session_key = f"comment_vote_{comment_id}"
                previous_action = request.session.get(session_key)

                if previous_action == action:
                    apps_logger.warning(
                        "Duplicate vote attempt",
                        extra={
                            "task_name": TaskName.PRODUCT_COMMENT_VOTE_DUPLICATE,
                            "user_id": request.user.id,
                            "comment_id": comment.id,
                            "action": action,
                            "correlation_id": getattr(
                                request, "correlation_id", None
                            ),
                        },
                    )
                    return JsonResponse(
                        {
                            "status": "error",
                            "message": "شما قبلاً این عمل را انجام داده‌اید.",
                        },
                        status=400,
                    )

                if previous_action == "like" and action == "dislike":
                    if comment.likes > 0:
                        comment.likes -= 1
                    comment.dislikes += 1
                    apps_logger.info(
                        "Vote switched from like to dislike",
                        extra={
                            "task_name": TaskName.PRODUCT_COMMENT_VOTE_SWITCH,
                            "user_id": request.user.id,
                            "comment_id": comment.id,
                            "from_action": "like",
                            "to_action": "dislike",
                            "likes": comment.likes,
                            "dislikes": comment.dislikes,
                            "correlation_id": getattr(
                                request, "correlation_id", None
                            ),
                        },
                    )

                elif previous_action == "dislike" and action == "like":
                    if comment.dislikes > 0:
                        comment.dislikes -= 1
                    comment.likes += 1
                    apps_logger.info(
                        "Vote switched from dislike to like",
                        extra={
                            "task_name": TaskName.PRODUCT_COMMENT_VOTE_SWITCH,
                            "user_id": request.user.id,
                            "comment_id": comment.id,
                            "from_action": "dislike",
                            "to_action": "like",
                            "likes": comment.likes,
                            "dislikes": comment.dislikes,
                            "correlation_id": getattr(
                                request, "correlation_id", None
                            ),
                        },
                    )

                elif previous_action is None:
                    if action == "like":
                        comment.likes += 1
                    else:
                        comment.dislikes += 1
                    apps_logger.info(
                        "New vote registered",
                        extra={
                            "task_name": TaskName.PRODUCT_COMMENT_VOTE_NEW,
                            "user_id": request.user.id,
                            "comment_id": comment.id,
                            "action": action,
                            "likes": comment.likes,
                            "dislikes": comment.dislikes,
                            "correlation_id": getattr(
                                request, "correlation_id", None
                            ),
                        },
                    )

                comment.save()
                request.session[session_key] = action
                request.session.modified = True

                return JsonResponse(
                    {
                        "status": "success",
                        "message": "رأی شما ثبت شد.",
                        "likes": comment.likes,
                        "dislikes": comment.dislikes,
                    }
                )

        except ProductCommentModel.DoesNotExist:
            apps_logger.error(
                "Vote failed: comment not found",
                extra={
                    "task_name": TaskName.PRODUCT_COMMENT_VOTE_ERROR,
                    "user_id": request.user.id,
                    "comment_id": comment_id,
                    "action": action,
                    "correlation_id": getattr(request, "correlation_id", None),
                },
            )
            return JsonResponse(
                {"status": "error", "message": "کامنت یافت نشد."}, status=404
            )

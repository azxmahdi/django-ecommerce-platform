from enum import Enum


class TaskName(str, Enum):
    LOGIN = "login"
    LOGIN_PASSWORD = "login_password"
    LOGIN_OTP = "login_otp"
    LOGOUT = "logout"

    AUTHENTICATION = "authentication"
    OTP_VERIFICATION = "otp_verification"
    SEND_OTP = "send_otp"
    SIGNUP_OTP = "signup_otp"
    FORGOT_OTP = "forgot_otp"

    SET_PASSWORD = "set_password"
    PASSWORD_RESET = "password_reset"

    CART_ITEM_ADD = "cart_item_add"
    CART_ITEM_UPDATE = "cart_item_update"
    CART_ITEM_REMOVE = "cart_item_remove"
    CART_ITEM_CLEAR = "cart_item_remove"
    CART_SYNC = "cart_sync"
    CART_MERGE = "cart_merge"

    COUPON_APPLY = "coupon_apply"

    REPAYMENT = "repayment"
    GENERATE_PAYMENT_URL = "generate_payment_url"
    GET_DOMAIN = "get_domain"
    PAYMENT_REQUEST = "payment_request"
    PAYMENT_VERIFY = "payment_verify"

    PROFILE_EDIT_NAME = "profile_edit_name"
    PROFILE_EDIT_PASSWORD = "profile_edit_password"
    PROFILE_EDIT_PHONE = "profile_edit_phone"
    PROFILE_VERIFY_PHONE = "profile_verify_phone"
    PAYMENT_CREATE = "payment_create"
    PAYMENT_INITIATE = "payment_initiate"
    PAYMENT_GET_BY_AUTHORITY = "payment_get_by_authority"
    CHECKOUT_PAYMENT = "checkout_payment"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    PAYMENT_PROCESS = "payment_process"

    ORDER_VALIDATE_STOCK = "order_validate_stock"
    ORDER_UPDATE_CART_ITEMS = "order_update_cart_items"
    ORDER_CREATE_ITEMS = "order_create_items"
    ORDER_VALIDATE_AND_CREATE = "order_validate_and_create"
    ORDER_TRY_GET = "order_try_get"
    ORDER_UPDATE_STATUS = "order_update_status"
    ORDER_CHECKOUT_SHIPPING = "order_checkout_shipping"

    ADDRESS_CREATE = "address_create"
    ADDRESS_DELETE = "address_delete"
    ADDRESS_EDIT = "address_edit"

    APPLY_SHIPPING_METHOD = "apply_shipping_method"

    PRODUCT_COMMENT_SUBMIT = "product_comment_submit"
    PRODUCT_COMMENT_VOTE_ERROR = "product_comment_vote_error"
    PRODUCT_COMMENT_VOTE_DUPLICATE = "product_comment_vote_duplicate"
    PRODUCT_COMMENT_VOTE_SWITCH = "product_comment_vote_switch"
    PRODUCT_COMMENT_VOTE_NEW = "product_comment_vote_new"

    PRODUCT_VARIANT = "product_variant"

    CATEGORY_CACHE_INVALIDATE = "category_cache_invalidate"

    SITE_INFO_CACHE_INVALIDATE = "site_info_cache_invalidate"
    SITE_RESOURCE_CACHE_INVALIDATE = "site_resource_cache_invalidate"

    WISHLIST_REMOVE = "wishlist_remove"
    WISHLIST_ADD = "wishlist_add"
    WISHLIST_ERROR = "wishlist_error"
    WISHLIST_REMOVE_ALL = "wishlist_remove_all"


class LoggerName(str, Enum):
    AUTHENTICATION = "authentication"
    SECURITY = "security"
    OTP = "otp"
    PAYMENT = "payment"
    APPS = "apps"

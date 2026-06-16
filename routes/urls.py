from flask import Blueprint, request, jsonify, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import Config
import models.user as UserModel
import models.url as UrlModel

urls_bp = Blueprint("urls", __name__)


@urls_bp.route("/api/shorten", methods=["POST"])
@jwt_required()
def shorten():
    """
    Create a shortened URL.

    Headers:
        Authorization: Bearer <token>

    Request (JSON):
        { "url": "https://example.com/very/long/path" }

    Responses:
        201 - Short URL created
        400 - Invalid URL or missing data
        401 - Missing/invalid token
        500 - Server error
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    original_url = data.get("url", "").strip()

    if not original_url:
        return jsonify({"error": "url is required"}), 400

    if len(original_url) > Config.MAX_URL_LENGTH:
        return jsonify({
            "error": f"URL exceeds maximum length of {Config.MAX_URL_LENGTH} characters"
        }), 400

    if not (original_url.startswith("http://") or original_url.startswith("https://")):
        return jsonify({"error": "URL must start with http:// or https://"}), 400

    current_email = get_jwt_identity()
    user = UserModel.get_public_user_by_email(current_email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    try:
        url = UrlModel.create_url(user["id"], original_url)
        return jsonify({
            "message": "URL shortened successfully",
            "url": url
        }), 201
    except Exception as e:
        return jsonify({"error": "Failed to shorten URL", "details": str(e)}), 500


@urls_bp.route("/api/urls", methods=["GET"])
@jwt_required()
def list_urls():
    """
    List all URLs created by the authenticated user.

    Headers:
        Authorization: Bearer <token>

    Responses:
        200 - List of user's URLs
        401 - Missing/invalid token
        404 - User not found
    """
    current_email = get_jwt_identity()
    user = UserModel.get_public_user_by_email(current_email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    urls = UrlModel.get_urls_by_user(user["id"])
    return jsonify({
        "total": len(urls),
        "urls": urls
    }), 200


@urls_bp.route("/api/analytics", methods=["GET"])
@jwt_required()
def analytics():
    """
    Get detailed click analytics for the authenticated user's URLs.

    Headers:
        Authorization: Bearer <token>

    Responses:
        200 - Analytics data with top URLs
        401 - Missing/invalid token
        404 - User not found
    """
    current_email = get_jwt_identity()
    user = UserModel.get_public_user_by_email(current_email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    analytics_data = UrlModel.get_user_analytics(user["id"])
    return jsonify(analytics_data), 200


@urls_bp.route("/api/urls/<int:url_id>", methods=["DELETE"])
@jwt_required()
def delete_url_route(url_id):
    """
    Delete a URL owned by the authenticated user.

    Headers:
        Authorization: Bearer <token>

    Responses:
        200 - URL deleted successfully
        401 - Missing/invalid token
        404 - URL not found or not owned by user
    """
    current_email = get_jwt_identity()
    user = UserModel.get_public_user_by_email(current_email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    deleted = UrlModel.delete_url(url_id, user["id"])
    if not deleted:
        return jsonify({"error": "URL not found or not owned by user"}), 404

    return jsonify({"message": "URL deleted successfully"}), 200


@urls_bp.route("/<code>", methods=["GET"])
def redirect_short_url(code):
    """
    Redirect a short code to the original URL.

    This route does not require authentication — anyone can follow a short link.
    """
    url = UrlModel.get_url_by_code(code)
    if not url:
        return jsonify({"error": "URL not found"}), 404

    UrlModel.increment_clicks(code)
    return redirect(url["original_url"], 302)

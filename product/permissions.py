from rest_framework import permissions


class AuthorModifyOrReadOnly1(permissions.IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # إذا لم يكن المستخدم مسجلاً، فلا يُسمح له بالتعديل
        if not request.user or not request.user.is_authenticated:
            return False

        # إذا كان المستخدم هو صاحب المنتج (post)، يُسمح له بالتعديل على كل شيء
        if request.user == obj.user:
            return True

        # إذا لم يكن المستخدم صاحب المنتج، فيمكنه تعديل حقل comment فقط.
        # نحصل على مفاتيح الحقول المرسلة في الطلب
        allowed_fields = {'comment'}
        data_keys = set(request.data.keys())
        
        # الشروط: إذا كانت مجموعة الحقول المرسلة ضمن الحقول المسموحة، نسمح له بالتعديل،
        # وإلا نرفض الإذن.
        return data_keys.issubset(allowed_fields)
class AuthorModifyOrReadOnly2(permissions.IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return  request.user == obj
    

class IsCommentCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        print(obj.creator.username)
        print(request.user)
        return obj.creator == request.user    
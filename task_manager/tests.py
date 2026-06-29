from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from hr.models import Employee, EmployeeRole
from task_manager.models import PlannedTask, DailyTask
from users.models import CustomUser


class TaskManagerTestBase(APITestCase):
    """Shared fixtures for all task_manager tests."""

    @classmethod
    def setUpTestData(cls):
        cls.rw_role = EmployeeRole.objects.create(
            role_name="Manager",
            description="Full access",
            can_read_task_manager=True,
            can_write_task_manager=True,
        )
        cls.basic_role = EmployeeRole.objects.create(
            role_name="Basic",
            description="No task-manager access",
            can_read_task_manager=False,
            can_write_task_manager=False,
        )

        cls.manager_user = CustomUser.objects.create_user(phone="09120000001")
        cls.basic_user = CustomUser.objects.create_user(phone="09120000002")

        cls.manager_emp = Employee.objects.create(
            user=cls.manager_user,
            role=cls.rw_role,
            first_name="Ali",
            last_name="Manager",
        )
        cls.basic_emp = Employee.objects.create(
            user=cls.basic_user,
            role=cls.basic_role,
            first_name="Reza",
            last_name="Basic",
        )

    def auth_manager(self):
        self.client.force_authenticate(user=self.manager_user)

    def auth_basic(self):
        self.client.force_authenticate(user=self.basic_user)

    def unauth(self):
        self.client.force_authenticate(user=None)


# ─── PlannedTask Dashboard ────────────────────────────────────────────────────
class PlannedTaskDashboardTests(TaskManagerTestBase):

    def setUp(self):
        PlannedTask.objects.create(
            employee=self.basic_emp, title="Basic planned",
            status="planed", priority="medium", type="Personal",
        )
        PlannedTask.objects.create(
            employee=self.manager_emp, title="Manager planned",
            status="in_progress", priority="high", type="Personal",
        )
        PlannedTask.objects.create(
            employee=self.manager_emp, title="Manager done",
            status="done", priority="low", type="Personal",
        )
        PlannedTask.objects.create(
            employee=self.basic_emp, title="Expired task",
            status="planed", priority="medium", type="Personal",
            deadline=timezone.now() - timedelta(days=1),
        )

    def test_unauthenticated_returns_401(self):
        self.unauth()
        resp = self.client.get(reverse("task-manager-stats"))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_basic_employee_sees_only_my_tasks(self):
        self.auth_basic()
        resp = self.client.get(reverse("task-manager-stats"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNone(resp.data["all_tasks"])
        self.assertEqual(resp.data["my_tasks"]["not_started"], 2)

    def test_manager_sees_all_tasks(self):
        self.auth_manager()
        resp = self.client.get(reverse("task-manager-stats"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(resp.data["all_tasks"])
        self.assertEqual(resp.data["all_tasks"]["done"], 1)

    def test_permissions_in_response(self):
        self.auth_manager()
        resp = self.client.get(reverse("task-manager-stats"))
        self.assertTrue(resp.data["permissions"]["can_read_task_manager"])
        self.assertTrue(resp.data["permissions"]["can_write_task_manager"])

    def test_basic_permissions_in_response(self):
        self.auth_basic()
        resp = self.client.get(reverse("task-manager-stats"))
        self.assertFalse(resp.data["permissions"]["can_read_task_manager"])
        self.assertFalse(resp.data["permissions"]["can_write_task_manager"])


# ─── Task Choices ─────────────────────────────────────────────────────────────
class TaskChoicesTests(TaskManagerTestBase):

    def test_unauthenticated_returns_401(self):
        self.unauth()
        resp = self.client.get(reverse("task-choices"))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_choices(self):
        self.auth_basic()
        resp = self.client.get(reverse("task-choices"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("employees", resp.data)
        self.assertIn("status_choices", resp.data)
        self.assertIn("priority_choices", resp.data)
        self.assertIn("type_choices", resp.data)

    def test_employees_list_excludes_deleted(self):
        deleted_user = CustomUser.objects.create_user(phone="09120000099")
        Employee.objects.create(
            user=deleted_user, role=self.basic_role,
            first_name="Deleted", last_name="Emp", is_deleted=True,
        )
        self.auth_basic()
        resp = self.client.get(reverse("task-choices"))
        ids = [e["id"] for e in resp.data["employees"]]
        self.assertNotIn(deleted_user.employee.id, ids)


# ─── PlannedTask Search ──────────────────────────────────────────────────────
class PlannedTaskSearchTests(TaskManagerTestBase):

    def setUp(self):
        self.t1 = PlannedTask.objects.create(
            employee=self.basic_emp, title="Fix login bug",
            status="planed", priority="high", type="Personal",
        )
        self.t2 = PlannedTask.objects.create(
            employee=self.manager_emp, title="Organize meeting",
            status="in_progress", priority="medium", type="Organize",
        )

    def test_basic_only_sees_own(self):
        self.auth_basic()
        resp = self.client.get(reverse("task-search"), {"q": "Fix"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        titles = [t["title"] for t in resp.data["results"]]
        self.assertIn("Fix login bug", titles)

    def test_basic_cannot_see_organize(self):
        self.auth_basic()
        resp = self.client.get(reverse("task-search"), {"q": "Organize"})
        titles = [t["title"] for t in resp.data["results"]]
        self.assertNotIn("Organize meeting", titles)

    def test_manager_sees_organize(self):
        self.auth_manager()
        resp = self.client.get(reverse("task-search"), {"q": "Organize"})
        titles = [t["title"] for t in resp.data["results"]]
        self.assertIn("Organize meeting", titles)


# ─── PlannedTask List ────────────────────────────────────────────────────────
class PlannedTaskListTests(TaskManagerTestBase):

    def setUp(self):
        self.personal = PlannedTask.objects.create(
            employee=self.basic_emp, title="My personal",
            status="planed", priority="low", type="Personal",
        )
        self.organize = PlannedTask.objects.create(
            employee=self.manager_emp, title="Org task",
            status="done", priority="high", type="Organize",
        )
        self.other_personal = PlannedTask.objects.create(
            employee=self.manager_emp, title="Manager personal",
            status="in_progress", priority="medium", type="Personal",
        )

    def test_basic_sees_only_own(self):
        self.auth_basic()
        resp = self.client.get(reverse("task-list"))
        titles = [t["title"] for t in resp.data["results"]]
        self.assertIn("My personal", titles)
        self.assertNotIn("Manager personal", titles)
        self.assertNotIn("Org task", titles)

    def test_manager_sees_own_and_organize(self):
        self.auth_manager()
        resp = self.client.get(reverse("task-list"))
        titles = [t["title"] for t in resp.data["results"]]
        self.assertIn("Manager personal", titles)
        self.assertIn("Org task", titles)
        self.assertNotIn("My personal", titles)

    def test_filter_by_status(self):
        self.auth_basic()
        resp = self.client.get(reverse("task-list"), {"status": "planed"})
        self.assertTrue(all(t["status"] == "planed" for t in resp.data["results"]))

    def test_soft_deleted_not_shown(self):
        self.personal.is_deleted = True
        self.personal.save()
        self.auth_basic()
        resp = self.client.get(reverse("task-list"))
        ids = [t["id"] for t in resp.data["results"]]
        self.assertNotIn(self.personal.id, ids)


# ─── Personal PlannedTask CRUD ───────────────────────────────────────────────
class PersonalPlannedTaskCRUDTests(TaskManagerTestBase):

    def test_create_personal_task(self):
        self.auth_basic()
        data = {
            "title": "New personal task",
            "description": "Test desc",
            "status": "planed",
            "priority": "medium",
        }
        resp = self.client.post(reverse("personal-task-create"), data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        task = PlannedTask.objects.get(id=resp.data["id"])
        self.assertEqual(task.employee, self.basic_emp)
        self.assertEqual(task.type, "Personal")

    def test_retrieve_own_personal_task(self):
        task = PlannedTask.objects.create(
            employee=self.basic_emp, title="My task",
            status="planed", priority="low", type="Personal",
        )
        self.auth_basic()
        resp = self.client.get(reverse("personal-task-rud", args=[task.pk]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["title"], "My task")

    def test_cannot_access_other_users_task(self):
        task = PlannedTask.objects.create(
            employee=self.manager_emp, title="Not yours",
            status="planed", priority="low", type="Personal",
        )
        self.auth_basic()
        resp = self.client.get(reverse("personal-task-rud", args=[task.pk]))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_personal_task(self):
        task = PlannedTask.objects.create(
            employee=self.basic_emp, title="Old title",
            status="planed", priority="low", type="Personal",
        )
        self.auth_basic()
        resp = self.client.patch(
            reverse("personal-task-rud", args=[task.pk]),
            {"title": "New title"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, "New title")

    def test_delete_is_soft_delete(self):
        task = PlannedTask.objects.create(
            employee=self.basic_emp, title="To delete",
            status="planed", priority="low", type="Personal",
        )
        self.auth_basic()
        resp = self.client.delete(reverse("personal-task-rud", args=[task.pk]))
        self.assertIn(resp.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT])
        task.refresh_from_db()
        self.assertTrue(task.is_deleted)

    def test_cannot_see_organize_task_via_personal_endpoint(self):
        task = PlannedTask.objects.create(
            employee=self.basic_emp, title="Org task",
            status="planed", priority="low", type="Organize",
        )
        self.auth_basic()
        resp = self.client.get(reverse("personal-task-rud", args=[task.pk]))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


# ─── Organize PlannedTask CRUD ───────────────────────────────────────────────
class OrganizePlannedTaskCRUDTests(TaskManagerTestBase):

    def test_create_requires_write_permission(self):
        self.auth_basic()
        data = {
            "employee": self.basic_emp.pk,
            "title": "New org task",
            "status": "planed",
            "priority": "high",
        }
        resp = self.client.post(reverse("organize-task-create"), data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_with_write_permission(self):
        self.auth_manager()
        data = {
            "employee": self.basic_emp.pk,
            "title": "New org task",
            "status": "planed",
            "priority": "high",
        }
        resp = self.client.post(reverse("organize-task-create"), data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        task = PlannedTask.objects.get(id=resp.data["id"])
        self.assertEqual(task.type, "Organize")

    def test_retrieve_organize_task(self):
        task = PlannedTask.objects.create(
            employee=self.basic_emp, title="Org detail",
            status="planed", priority="low", type="Organize",
        )
        self.auth_basic()
        resp = self.client.get(reverse("organize-task-rud", args=[task.pk]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_patch_requires_write_permission(self):
        task = PlannedTask.objects.create(
            employee=self.basic_emp, title="Org task",
            status="planed", priority="low", type="Organize",
        )
        self.auth_basic()
        resp = self.client.patch(
            reverse("organize-task-rud", args=[task.pk]),
            {"title": "Changed"},
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_with_write_permission(self):
        task = PlannedTask.objects.create(
            employee=self.basic_emp, title="Org task",
            status="planed", priority="low", type="Organize",
        )
        self.auth_manager()
        resp = self.client.patch(
            reverse("organize-task-rud", args=[task.pk]),
            {"title": "Updated"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, "Updated")

    def test_delete_requires_write_permission(self):
        task = PlannedTask.objects.create(
            employee=self.basic_emp, title="Org task",
            status="planed", priority="low", type="Organize",
        )
        self.auth_basic()
        resp = self.client.delete(reverse("organize-task-rud", args=[task.pk]))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_soft_deletes(self):
        task = PlannedTask.objects.create(
            employee=self.basic_emp, title="Org task",
            status="planed", priority="low", type="Organize",
        )
        self.auth_manager()
        resp = self.client.delete(reverse("organize-task-rud", args=[task.pk]))
        self.assertIn(resp.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT])
        task.refresh_from_db()
        self.assertTrue(task.is_deleted)


# ─── Pending Approval + Approve/Reject ───────────────────────────────────────
class PendingApprovalTests(TaskManagerTestBase):

    def setUp(self):
        self.pending = PlannedTask.objects.create(
            employee=self.basic_emp, title="Pending reward",
            status="done", priority="high", type="Organize",
            has_reward=True, reward_amount=100000, approved=False,
        )
        self.not_pending = PlannedTask.objects.create(
            employee=self.basic_emp, title="Already approved",
            status="done", priority="high", type="Organize",
            has_reward=True, reward_amount=50000, approved=True,
        )

    def test_list_pending_approval(self):
        self.auth_manager()
        resp = self.client.get(reverse("pending-approval-list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ids = [t["id"] for t in resp.data["results"]]
        self.assertIn(self.pending.id, ids)
        self.assertNotIn(self.not_pending.id, ids)

    def test_approve_task(self):
        self.auth_manager()
        resp = self.client.post(reverse("task-approve", args=[self.pending.pk]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.pending.refresh_from_db()
        self.assertTrue(self.pending.approved)

    def test_reject_task_resets_status(self):
        self.auth_manager()
        resp = self.client.post(reverse("task-reject", args=[self.pending.pk]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.pending.refresh_from_db()
        self.assertEqual(self.pending.status, "in_progress")
        self.assertFalse(self.pending.approved)

    def test_approve_already_approved_returns_404(self):
        self.auth_manager()
        resp = self.client.post(reverse("task-approve", args=[self.not_pending.pk]))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


# ─── DailyTask List ──────────────────────────────────────────────────────────
class DailyTaskListTests(TaskManagerTestBase):

    def setUp(self):
        self.dt1 = DailyTask.objects.create(title="Basic daily", type="Personal")
        self.dt1.employees.add(self.basic_emp)

        self.dt2 = DailyTask.objects.create(title="Org daily", type="Organize")
        self.dt2.employees.add(self.manager_emp)

    def test_unauthenticated_returns_401(self):
        self.unauth()
        resp = self.client.get(reverse("daily-task-list"))
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_basic_sees_only_own(self):
        self.auth_basic()
        resp = self.client.get(reverse("daily-task-list"))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        titles = [t["title"] for t in resp.data["results"]]
        self.assertIn("Basic daily", titles)

    def test_manager_sees_all(self):
        self.auth_manager()
        resp = self.client.get(reverse("daily-task-list"))
        titles = [t["title"] for t in resp.data["results"]]
        self.assertIn("Basic daily", titles)
        self.assertIn("Org daily", titles)

    def test_soft_deleted_not_shown(self):
        self.dt1.is_deleted = True
        self.dt1.save()
        self.auth_basic()
        resp = self.client.get(reverse("daily-task-list"))
        ids = [t["id"] for t in resp.data["results"]]
        self.assertNotIn(self.dt1.id, ids)


# ─── DailyTask Search ────────────────────────────────────────────────────────
class DailyTaskSearchTests(TaskManagerTestBase):

    def setUp(self):
        self.dt1 = DailyTask.objects.create(title="Fix server", type="Personal")
        self.dt1.employees.add(self.basic_emp)

        self.dt2 = DailyTask.objects.create(title="Deploy app", type="Organize")
        self.dt2.employees.add(self.manager_emp)

    def test_search_by_title(self):
        self.auth_basic()
        resp = self.client.get(reverse("daily-task-search"), {"search": "Fix"})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_unauthenticated_returns_401(self):
        self.unauth()
        resp = self.client.get(reverse("daily-task-search"), {"search": "Fix"})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


# ─── Personal DailyTask CRUD ─────────────────────────────────────────────────
class PersonalDailyTaskCRUDTests(TaskManagerTestBase):

    def test_create_personal_daily_task(self):
        self.auth_basic()
        data = {
            "employee": self.basic_emp.pk,
            "title": "New daily",
            "description": "Daily desc",
        }
        resp = self.client.post(reverse("personal-daily-task-add"), data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        task = DailyTask.objects.get(title="New daily")
        self.assertEqual(task.type, "Personal")
        self.assertIn(self.basic_emp, task.employees.all())

    def test_retrieve_own_daily_task(self):
        task = DailyTask.objects.create(title="My daily", type="Personal")
        task.employees.add(self.basic_emp)
        self.auth_basic()
        resp = self.client.get(reverse("personal-daily-task-rud", args=[task.pk]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_cannot_access_other_users_daily_task(self):
        task = DailyTask.objects.create(title="Not mine", type="Personal")
        task.employees.add(self.manager_emp)
        self.auth_basic()
        resp = self.client.get(reverse("personal-daily-task-rud", args=[task.pk]))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_is_soft_delete(self):
        task = DailyTask.objects.create(title="Delete me", type="Personal")
        task.employees.add(self.basic_emp)
        self.auth_basic()
        resp = self.client.delete(reverse("personal-daily-task-rud", args=[task.pk]))
        self.assertIn(resp.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT])
        task.refresh_from_db()
        self.assertTrue(task.is_deleted)

    def test_cannot_see_organize_via_personal_endpoint(self):
        task = DailyTask.objects.create(title="Org task", type="Organize")
        task.employees.add(self.basic_emp)
        self.auth_basic()
        resp = self.client.get(reverse("personal-daily-task-rud", args=[task.pk]))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


# ─── Organize DailyTask CRUD ─────────────────────────────────────────────────
class OrganizeDailyTaskCRUDTests(TaskManagerTestBase):

    def test_create_requires_write_permission(self):
        self.auth_basic()
        data = {
            "employees": [self.basic_emp.pk],
            "title": "Org daily",
            "description": "Desc",
        }
        resp = self.client.post(reverse("organize-daily-task-add"), data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_with_write_permission(self):
        self.auth_manager()
        data = {
            "employees": [self.basic_emp.pk, self.manager_emp.pk],
            "title": "Org daily",
            "description": "Desc",
        }
        resp = self.client.post(reverse("organize-daily-task-add"), data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        task = DailyTask.objects.get(title="Org daily")
        self.assertEqual(task.type, "Organize")
        self.assertEqual(task.employees.count(), 2)

    def test_retrieve_organize_daily_task(self):
        task = DailyTask.objects.create(title="Org detail", type="Organize")
        task.employees.add(self.basic_emp)
        self.auth_basic()
        resp = self.client.get(reverse("organize-daily-task-rud", args=[task.pk]))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_update_requires_write_permission(self):
        task = DailyTask.objects.create(title="Org task", type="Organize")
        task.employees.add(self.basic_emp)
        self.auth_basic()
        resp = self.client.patch(
            reverse("organize-daily-task-rud", args=[task.pk]),
            {"title": "Changed"},
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_with_write_permission(self):
        task = DailyTask.objects.create(title="Org task", type="Organize")
        task.employees.add(self.basic_emp)
        self.auth_manager()
        resp = self.client.patch(
            reverse("organize-daily-task-rud", args=[task.pk]),
            {"title": "Updated"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, "Updated")

    def test_delete_requires_write_permission(self):
        task = DailyTask.objects.create(title="Org task", type="Organize")
        task.employees.add(self.basic_emp)
        self.auth_basic()
        resp = self.client.delete(reverse("organize-daily-task-rud", args=[task.pk]))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_soft_deletes(self):
        task = DailyTask.objects.create(title="Org task", type="Organize")
        task.employees.add(self.basic_emp)
        self.auth_manager()
        resp = self.client.delete(reverse("organize-daily-task-rud", args=[task.pk]))
        self.assertIn(resp.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT])
        task.refresh_from_db()
        self.assertTrue(task.is_deleted)

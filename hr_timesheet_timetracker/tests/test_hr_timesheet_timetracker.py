# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from psycopg2 import IntegrityError
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common
from odoo.tools.misc import mute_logger


class TestHrTimesheetTimetracker(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.now = fields.Datetime.now()
        self.uom_hour = self.env.ref('uom.product_uom_hour')
        self.Project = self.env['project.project']
        self.SudoProject = self.Project.sudo()
        self.Task = self.env['project.task']
        self.SudoTask = self.Task.sudo()
        self.HrEmployee = self.env['hr.employee']
        self.SudoHrEmployee = self.HrEmployee.sudo()
        self.AccountAnalyticLine = self.env['account.analytic.line']
        self.SudoAccountAnalyticLine = self.AccountAnalyticLine.sudo()
        self.User = self.env['res.users']
        self.SudoUser = self.User.sudo()

    def test_1(self):
        project = self.SudoProject.create({
            'name': 'Project #1',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #1',
            'user_id': self.env.user.id,
        })
        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #1',
            'employee_id': employee.id,
        })

        entry.timetracker_started_at = self.now - relativedelta(hours=1)

        self.assertEqual(entry.is_timetracker_running, True)

    def test_2(self):
        project = self.SudoProject.create({
            'name': 'Project #2',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #2',
            'user_id': self.env.user.id,
        })
        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #2',
            'employee_id': employee.id,
        })

        entry.timetracker_started_at = self.now - relativedelta(hours=1)
        entry.timetracker_stopped_at = self.now

        self.assertEqual(entry.is_timetracker_running, False)

    def test_3(self):
        project = self.SudoProject.create({
            'name': 'Project #3',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #3',
            'user_id': self.env.user.id,
        })
        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #3',
            'employee_id': employee.id,
        })

        entry.timetracker_started_at = self.now

        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            entry.timetracker_stopped_at = self.now - relativedelta(hours=1)

    def test_4(self):
        project = self.SudoProject.create({
            'name': 'Project #4',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #4',
            'user_id': self.env.user.id,
        })
        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #4',
            'employee_id': employee.id,
        })

        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            entry.timetracker_stopped_at = self.now - relativedelta(hours=1)

    def test_5(self):
        project = self.SudoProject.create({
            'name': 'Project #5',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #5',
            'user_id': self.env.user.id,
        })
        t = self.now.replace(
            minute=0,
            second=0,
            microsecond=0,
        )
        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #5',
            'employee_id': employee.id,
            'timetracker_started_at': t - relativedelta(hours=2),
            'timetracker_stopped_at': t,
        })

        entry.unit_amount = 1.0
        self.assertEqual(
            entry.timetracker_stopped_at,
            t - relativedelta(hours=1)
        )

    def test_6(self):
        project = self.SudoProject.create({
            'name': 'Project #6',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #6',
            'user_id': self.env.user.id,
        })
        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #6',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
            'timetracker_stopped_at': self.now,
        })

        entry.timetracker_started_at = self.now - relativedelta(hours=1)

    def test_7(self):
        project = self.SudoProject.create({
            'name': 'Project #7',
            'timetracker_rounding_enabled': False,
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #7',
            'user_id': self.env.user.id,
        })
        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #7',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
            'timetracker_stopped_at': self.now,
        })

        self.assertEqual(entry.unit_amount, 2.0)
        entry.timetracker_stopped_at = self.now - relativedelta(hours=1)
        self.assertEqual(entry.unit_amount, 1.0)

    def test_8(self):
        project = self.SudoProject.create({
            'name': 'Project #8',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #8',
            'user_id': self.env.user.id,
        })

        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.SudoAccountAnalyticLine.create({
                'project_id': project.id,
                'name': 'Time Entry #8',
                'employee_id': employee.id,
                'timetracker_stopped_at': self.now,
            })

    def test_9(self):
        project = self.SudoProject.create({
            'name': 'Project #9',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #9',
            'user_id': self.env.user.id,
        })

        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.SudoAccountAnalyticLine.create({
                'project_id': project.id,
                'name': 'Time Entry #9',
                'employee_id': employee.id,
                'timetracker_started_at': self.now,
                'timetracker_stopped_at': self.now - relativedelta(hours=1),
            })

    def test_10(self):
        project = self.SudoProject.create({
            'name': 'Project #10',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #10',
            'user_id': self.env.user.id,
        })

        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.SudoAccountAnalyticLine.create({
                'project_id': project.id,
                'name': 'Time Entry #10',
                'employee_id': employee.id,
                'timetracker_started_at': self.now,
                'timetracker_stopped_at': self.now - relativedelta(hours=1),
                'unit_amount': 1.0,
            })

    def test_11(self):
        project = self.SudoProject.create({
            'name': 'Project #11',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #11',
            'user_id': self.env.user.id,
        })

        self.SudoAccountAnalyticLine.create([{
            'project_id': project.id,
            'name': 'Time Entry #11-1',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=1),
            'timetracker_stopped_at': self.now,
        }, {
            'project_id': project.id,
            'name': 'Time Entry #11-2',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
            'timetracker_stopped_at': self.now,
        }])

        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.SudoAccountAnalyticLine.create([{
                'project_id': project.id,
                'name': 'Time Entry #11-3',
                'employee_id': employee.id,
                'timetracker_started_at': self.now - relativedelta(hours=1),
            }, {
                'project_id': project.id,
                'name': 'Time Entry #11-4',
                'employee_id': employee.id,
                'timetracker_started_at': self.now - relativedelta(hours=2),
            }])

    def test_12(self):
        project = self.SudoProject.create({
            'name': 'Project #12',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #12',
            'user_id': self.env.user.id,
        })

        self.SudoAccountAnalyticLine.create([{
            'project_id': project.id,
            'name': 'Time Entry #12-1',
            'employee_id': employee.id,
            'unit_amount': 1,
        }, {
            'project_id': project.id,
            'name': 'Time Entry #12-2',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
            'timetracker_stopped_at': self.now,
        }])

    def test_13(self):
        project = self.SudoProject.create({
            'name': 'Project #13',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #13',
            'user_id': self.env.user.id,
        })

        entry_1 = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #13-1',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
        })

        entry_2 = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #13-2',
            'employee_id': employee.id,
        })

        currently_timetracked_default = (
            self.SudoAccountAnalyticLine.get_currently_timetracked()
        )
        self.assertIn(entry_1, currently_timetracked_default)
        self.assertNotIn(entry_2, currently_timetracked_default)

        currently_timetracked_by_user = (
            self.SudoAccountAnalyticLine.get_currently_timetracked(
                self.env.user
            )
        )
        self.assertIn(entry_1, currently_timetracked_by_user)
        self.assertNotIn(entry_2, currently_timetracked_by_user)

        currently_timetracked_by_users = (
            self.SudoAccountAnalyticLine.get_currently_timetracked(
                self.User.browse()
            )
        )
        self.assertIn(entry_1, currently_timetracked_by_users)
        self.assertNotIn(entry_2, currently_timetracked_by_users)

        entry_2.action_timetracker()

        self.assertEqual(entry_1.is_timetracker_running, False)
        self.assertEqual(entry_2.is_timetracker_running, True)

        with self.assertRaises(ValidationError):
            entry_2.date = None

    def test_14(self):
        project = self.SudoProject.create({
            'name': 'Project #14',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #14',
            'user_id': self.env.user.id,
        })

        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #14',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
            'timetracker_stopped_at': self.now,
        })

        entry.action_timetracker()

        self.assertEqual(entry.is_timetracker_running, False)

        currently_timetracked = (
            self.SudoAccountAnalyticLine.get_currently_timetracked()
        )
        self.assertNotIn(entry, currently_timetracked)
        self.assertEquals(len(currently_timetracked), 1)
        self.assertEquals(currently_timetracked.project_id, entry.project_id)
        self.assertEquals(currently_timetracked.name, entry.name)
        self.assertEquals(currently_timetracked.timetracker_stopped_at, False)

    def test_15(self):
        project = self.SudoProject.create({
            'name': 'Project #15',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #15',
            'user_id': self.env.user.id,
        })

        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #15',
            'employee_id': employee.id,
            'timetracker_started_at': (
                self.now - relativedelta(hours=2)
            ).replace(
                minute=0,
                second=0,
                microsecond=0,
            ),
        })
        entry.timetracker_stopped_at = self.now.replace(
            minute=0,
            second=0,
            microsecond=0,
        )

        self.assertEqual(entry.unit_amount, 2.0)

    def test_16(self):
        project = self.SudoProject.create({
            'name': 'Project #16',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #16',
            'user_id': self.env.user.id,
        })

        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #16',
            'employee_id': employee.id,
            'timetracker_started_at': self.now.replace(
                minute=0,
                second=0,
                microsecond=0,
            ),
        })
        entry.timetracker_stopped_at = self.now.replace(
            minute=0,
            second=1,
            microsecond=0,
        )

        self.assertEqual(entry.unit_amount, 0.01)

    def test_17(self):
        project = self.SudoProject.create({
            'name': 'Project #17',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #17',
            'user_id': self.env.user.id,
        })

        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #17',
            'employee_id': employee.id,
            'timetracker_started_at': (
                self.now - relativedelta(hours=2)
            ).replace(
                minute=0,
                second=1,
                microsecond=0,
            ),
        })
        entry.timetracker_stopped_at = self.now.replace(
            minute=0,
            second=0,
            microsecond=0,
        ) - relativedelta(seconds=1)

        self.assertEqual(entry.unit_amount, 2.0)

    def test_18(self):
        project = self.SudoProject.create({
            'name': 'Project #18',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #18',
            'user_id': self.env.user.id,
        })

        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #18',
            'employee_id': employee.id,
            'timetracker_started_at': (
                self.now - relativedelta(hours=2)
            ).replace(
                minute=0,
                second=0,
                microsecond=0,
            ) - relativedelta(seconds=1),
        })
        entry.timetracker_stopped_at = self.now.replace(
            minute=0,
            second=0,
            microsecond=0,
        ) + relativedelta(seconds=1)

        self.assertEqual(entry.unit_amount, 2.02)

    def test_19(self):
        project = self.SudoProject.create({
            'name': 'Project #19',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #19',
            'user_id': self.env.user.id,
        })

        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #19',
            'employee_id': employee.id,
            'timetracker_started_at': (
                self.now - relativedelta(hours=2)
            ).replace(
                minute=0,
                second=0,
                microsecond=0,
            ) - relativedelta(seconds=1),
        })
        entry.timetracker_stopped_at = self.now.replace(
            minute=0,
            second=0,
            microsecond=0,
        ) + relativedelta(seconds=1)

        entry.reset_timetracked_duration()
        self.assertEqual(entry.unit_amount, 2.02)

    def test_20(self):
        project = self.SudoProject.create({
            'name': 'Project #20',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #20',
            'user_id': self.env.user.id,
        })

        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #20',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
            'timetracker_stopped_at': self.now,
        })

        entry.write({
            'timetracker_started_at': None,
            'timetracker_stopped_at': None,
            'unit_amount': 1.0,
        })
        self.assertEqual(entry.unit_amount, 1.0)

    def test_21(self):
        project = self.SudoProject.create({
            'name': 'Project #21',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #21',
            'user_id': self.env.user.id,
        })

        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #21',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
            'timetracker_stopped_at': self.now,
        })

        entry.write({
            'timetracker_started_at': None,
            'timetracker_stopped_at': None,
            'date': self.now.date(),
        })

    def test_22(self):
        project = self.SudoProject.create({
            'name': 'Project #22',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #22',
            'user_id': self.env.user.id,
        })

        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #22',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
            'timetracker_stopped_at': self.now,
        })

        entry.write({
            'unit_amount': 1,
        })

    def test_23(self):
        project = self.SudoProject.create({
            'name': 'Project #23',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #23',
            'user_id': self.env.user.id,
        })

        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #23',
            'employee_id': employee.id,
            'timetracker_started_at': self.now - relativedelta(hours=2),
            'timetracker_stopped_at': self.now,
        })

        entry.write({
            'unit_amount': 1,
            'timetracker_stopped_at': self.now - relativedelta(hours=1),
        })

    def test_24(self):
        project = self.SudoProject.create({
            'name': 'Project #24',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #24',
            'user_id': self.env.user.id,
        })
        t = self.now.replace(
            minute=0,
            second=0,
            microsecond=0,
        )
        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #24',
            'employee_id': employee.id,
            'timetracker_started_at': t - relativedelta(hours=4),
            'timetracker_stopped_at': t,
        })
        entry.write({
            'unit_amount': 2,
            'timetracker_stopped_at': t,
        })

        self.assertEqual(entry.unit_amount, 4.0)

    def test_25(self):
        project = self.SudoProject.create({
            'name': 'Project #25',
            'timetracker_started_at_rounding': 'HALF-UP',
            'timetracker_stopped_at_rounding': 'HALF-UP',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #25',
            'user_id': self.env.user.id,
        })

        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #25',
            'employee_id': employee.id,
            'timetracker_started_at': self.now.replace(minute=2, second=30),
            'timetracker_stopped_at': self.now.replace(minute=2, second=30),
        })

        self.assertEqual(entry.unit_amount, 0.0)

    def test_26(self):
        project = self.SudoProject.create({
            'name': 'Project #26',
            'timetracker_started_at_rounding': 'UP',
            'timetracker_stopped_at_rounding': 'DOWN',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #26',
            'user_id': self.env.user.id,
        })

        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #26',
            'employee_id': employee.id,
            'timetracker_started_at': self.now.replace(
                minute=0,
                second=0,
                microsecond=1000,
            ),
            'timetracker_stopped_at': self.now.replace(
                minute=0,
                second=0,
                microsecond=2000,
            ),
        })

        self.assertEqual(entry.unit_amount, 0.0)

    def test_27(self):
        project = self.SudoProject.create({
            'name': 'Project #27',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #27',
            'user_id': self.env.user.id,
        })
        t = self.now.replace(
            minute=0,
            second=0,
            microsecond=0,
        )
        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #27',
            'employee_id': employee.id,
            'timetracker_started_at': t - relativedelta(hours=4),
            'timetracker_stopped_at': t,
        })
        entry.write({
            'unit_amount': 1,
            'timetracker_stopped_at': t - relativedelta(hours=2),
        })

        self.assertEqual(entry.unit_amount, 2.0)

    def test_28(self):
        project = self.SudoProject.create({
            'name': 'Project #28',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #28',
            'user_id': self.env.user.id,
        })

        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #28',
            'employee_id': employee.id,
            'timetracker_started_at': self.now,
            'timetracker_stopped_at': self.now + relativedelta(hours=4),
        })
        entry.write({
            'unit_amount': 0,
        })

        self.assertEqual(entry.timetracker_stopped_at, self.now)

    def test_29(self):
        project = self.SudoProject.create({
            'name': 'Project #29',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #29',
            'user_id': self.env.user.id,
        })
        t = self.now.replace(
            minute=0,
            second=0,
            microsecond=0,
        )
        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #29',
            'employee_id': employee.id,
            'timetracker_started_at': t,
            'timetracker_stopped_at': t + relativedelta(hours=4),
        })

        base_unit_amount = entry.unit_amount
        half_of_atom = entry.product_uom_id.rounding / 2
        entry.write({
            'unit_amount': base_unit_amount + half_of_atom,
        })
        self.assertEqual(
            entry.unit_amount,
            base_unit_amount + entry.product_uom_id.rounding
        )

    def test_30(self):
        project = self.SudoProject.create({
            'name': 'Project #30',
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #30',
            'user_id': self.env.user.id,
        })
        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'name': 'Time Entry #30',
            'employee_id': employee.id,
            'timetracker_started_at': self.now.replace(
                hour=19,
                minute=53,
                second=22,
                microsecond=0,
            ),
        })
        entry.product_uom_id = self.uom_hour.copy({
            'name': 'Hour #30',
            'rounding': 0.1,
        })

        entry.timetracker_stopped_at = self.now.replace(
            hour=20,
            minute=11,
            second=22,
            microsecond=0,
        )
        self.assertEqual(entry.unit_amount, 0.4)

        entry.write({
            'unit_amount': 0.283,
        })
        self.assertEqual(entry.unit_amount, 0.3)

    def test_31(self):
        project = self.SudoProject.create({
            'name': 'Project #31',
        })
        task = self.SudoTask.create({
            'name': 'Task #31',
            'project_id': project.id,
            'user_id': self.env.user.id,
        })
        self.SudoHrEmployee.create({
            'name': 'Employee #31',
            'user_id': self.env.user.id,
        })

        task._compute_can_use_timetracker()
        self.assertEqual(task.can_use_timetracker, True)

        task._compute_is_timetracker_running()
        self.assertEqual(task.is_timetracker_running, False)

        task.action_start_timetracker()

        task._compute_is_timetracker_running()
        self.assertEqual(task.is_timetracker_running, False)

    def test_32(self):
        project = self.SudoProject.create({
            'name': 'Project #32',
        })
        task = self.SudoTask.create({
            'name': 'Task #32',
            'project_id': project.id,
            'user_id': self.env.user.id,
        })
        employee = self.SudoHrEmployee.create({
            'name': 'Employee #32',
            'user_id': self.env.user.id,
        })

        entry = self.SudoAccountAnalyticLine.create({
            'project_id': project.id,
            'task_id': task.id,
            'name': 'Time Entry #32',
            'employee_id': employee.id,
        })
        task._compute_is_timetracker_running()
        self.assertEqual(task.is_timetracker_running, False)

        entry.action_timetracker()
        task._compute_is_timetracker_running()
        self.assertEqual(task.is_timetracker_running, True)

        task.action_stop_timetracker()
        task._compute_is_timetracker_running()
        self.assertEqual(task.is_timetracker_running, False)
        self.assertEqual(entry.is_timetracker_running, False)

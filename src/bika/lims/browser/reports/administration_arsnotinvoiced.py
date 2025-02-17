# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

from bika.lims.workflow import getTransitionDate

from Products.CMFCore.utils import getToolByName
from bika.lims.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import t
from bika.lims.utils import formatDateQuery, formatDateParms
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements


class Report(BrowserView):
    implements(IViewView)
    template = ViewPageTemplateFile("templates/report_out.pt")

    def __init__(self, context, request, report=None):
        self.report = report
        BrowserView.__init__(self, context, request)

    def __call__(self):
        bc = getToolByName(self.context, 'bika_catalog')
        self.report_content = {}
        parm_lines = {}
        parms = []
        headings = {}
        headings['header'] = _("Samples not invoiced")
        headings['subheader'] = _(
            "Published Samples which have not been invoiced")

        count_all = 0

        query = {'portal_type': 'AnalysisRequest',
                 'getInvoiced': False,
                 'review_state': 'published',
                 'sort_order': 'reverse'}

        date_query = formatDateQuery(self.context, 'c_DatePublished')
        if date_query:
            query['getDatePublished'] = date_query
            pubished = formatDateParms(self.context, 'c_DatePublished')
        else:
            pubished = 'Undefined'
        parms.append(
            {'title': _('Published'),
             'value': pubished,
             'type': 'text'})

        parms.append(
            {'title': _('Active'),
             'value': 'Undefined',
             'type': 'text'})



        # and now lets do the actual report lines
        formats = {'columns': 6,
                   'col_heads': [_('Client'), \
                                 _('Request'), \
                                 _('Sample type'), \
                                 _('Sample point'), \
                                 _('Published'), \
                                 _('Amount'), \
                       ],
                   'class': '',
        }

        datalines = []
        clients = {}
        sampletypes = {}
        samplepoints = {}
        categories = {}
        services = {}

        for ar_proxy in bc(query):
            ar = ar_proxy.getObject()

            dataline = []

            dataitem = {'value': ar.aq_parent.Title()}
            dataline.append(dataitem)

            dataitem = {'value': ar.getId()}
            dataline.append(dataitem)

            dataitem = {'value': ar.getSampleTypeTitle()}
            dataline.append(dataitem)

            dataitem = {'value': ar.getSamplePointTitle()}
            dataline.append(dataitem)

            dataitem = {'value':
                        self.ulocalized_time(getTransitionDate(ar, 'publish'),
                                             long_format=True)}
            dataline.append(dataitem)

            dataitem = {'value': ar.getTotalPrice()}
            dataline.append(dataitem)

            datalines.append(dataline)

            count_all += 1

        # table footer data
        footlines = []
        footline = []
        footitem = {'value': _('Number of analyses retested for period'),
                    'colspan': 5,
                    'class': 'total_label'}
        footline.append(footitem)
        footitem = {'value': count_all}
        footline.append(footitem)
        footlines.append(footline)

        self.report_content = {
            'headings': headings,
            'parms': parms,
            'formats': formats,
            'datalines': datalines,
            'footings': footlines}

        return {'report_title': t(headings['header']),
                'report_data': self.template()}

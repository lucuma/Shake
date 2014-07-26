# -*- coding: utf-8 -*-
"""
    # Paginator
    
"""
from math import ceil


DEFAULT_PER_PAGE = 10


def sanitize_page_number(page):
    if page == 'last':
        return page
    if isinstance(page, basestring) and page.isdigit():
        page = int(page)
    if isinstance(page, int) and (page > 0):
        return page
    return 1


def get_page(request, page_field='page'):
    page = request.values.get(page_field, 1, type=int)
    return sanitize_page_number(page)


class Paginator(object):
    """Helper class to paginate data.
    You can construct it from any SQLAlchemy query object or other iterable.
    """

    def __init__(self, query, page=1, per_page=DEFAULT_PER_PAGE, total=None):
        # The unlimited query object that was used to create this
        # pagination object.
        self.query = query

        # The number of items to be displayed on a page.
        assert isinstance(per_page, int) and (per_page > 0), \
            '`per_page` must be a positive integer'
        self.per_page = per_page

        # The total number of items matching the query.
        if total is None:
            try:
                total = query.count()
            except (TypeError, AttributeError):
                total = query.__len__()
        self.total = total

        # The current page number (1 indexed)
        page = sanitize_page_number(page)
        if page == 'last':
            page = self.num_pages
        self.page = page

        # The number of items in the current page (could be less than per_page)
        if total > per_page * page:
            showing = per_page
        else:
            showing = total - per_page * (page - 1)
        self.showing = showing

    @property
    def num_pages(self):
        """The total number of pages."""
        return int(ceil(self.total / float(self.per_page)))

    @property
    def is_paginated(self):
        """True if a more than one page exists."""
        return self.num_pages > 1

    @property
    def has_prev(self):
        """True if a previous page exists."""
        return self.page > 1

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.num_pages

    @property
    def next_num(self):
        """Number of the next page."""
        return self.page + 1

    @property
    def prev_num(self):
        """Number of the previous page."""
        return self.page - 1

    @property
    def prev(self):
        """Returns a :class:`Paginator` object for the previous page."""
        if self.has_prev:
            return Paginator(self.query, self.page - 1, per_page=self.per_page)

    @property
    def next(self):
        """Returns a :class:`Paginator` object for the next page."""
        if self.has_next:
            return Paginator(self.query, self.page + 1, per_page=self.per_page)

    @property
    def start_index(self):
        """0-based index of the first element in the current page."""
        return (self.page - 1) * self.per_page

    @property
    def end_index(self):
        """0-based index of the last element in the current page."""
        end = self.start_index + self.per_page - 1
        return min(end, self.total - 1)
    
    @property
    def items(self):
        offset = (self.page - 1) * self.per_page
        return self.query.limit(self.per_page).offset(offset)

    def __iter__(self):
        for i in self.items:
            yield i

    @property
    def pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        """Iterates over the page numbers in the pagination.  The four
        parameters control the thresholds how many numbers should be produced
        from the sides:
        
        1..left_edge
        ...
        (current - left_current), current, (current + right_current)
        ...
        (num_pages - right_edge)..num_pages

        Example:

        1 2 ... 8 9 (10) 11 12 13 14 15 ... 19 20

        Skipped page numbers are represented as `None`.
        This is one way how you could render such a pagination in the views:

        .. sourcecode:: html+jinja

            {% macro render_paginator(paginator, endpoint) %}
              <ol class="paginator">
              {%- if paginator.has_prev %}
                <li><a href="{{ url_for(endpoint, page=paginator.prev_num) }}"
                 rel="me prev">«</a></li>
              {% else %}
                <li class="disabled"><span>«</span></li>
              {%- endif %}

              {%- for page in paginator.pages %}
                {% if page %}
                  {% if page != paginator.page %}
                    <li><a href="{{ url_for(endpoint, page=page) }}"
                     rel="me">{{ page }}</a></li>
                  {% else %}
                    <li class="current"><span>{{ page }}</span></li>
                  {% endif %}
                {% else %}
                  <li><span class=ellipsis>…</span></li>
                {% endif %}
              {%- endfor %}

              {%- if paginator.has_next %}
                <li><a href="{{ url_for(endpoint, page=paginator.next_num) }}"
                 rel="me next">»</a></li>
              {% else %}
                <li class="disabled"><span>»</span></li>
              {%- endif %}
              </ol>
            {% endmacro %}
        """
        last = 0
        for num in xrange(1, self.num_pages + 1):
            if ((num <= left_edge) or
              ((num >= self.page - left_current) and (num < self.page + right_current)) or
              (num > self.num_pages - right_edge)):
                if last + 1 != num:
                    yield None
                yield num
                last = num


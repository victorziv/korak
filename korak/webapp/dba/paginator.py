class Paginator:

    def __init__(self, query, page, per_page, total, items):
        self.query = query
        self.page = page
        self.per_page = per_page
        self.total = total
        self.items = items
    # ___________________________________

    @property
    def has_prev(self):
        return self.page > 1

def paginate_queryset(qs, offset=None, limit=None, ordering=None):
    count = qs.count()
    if ordering:
        qs = qs.order_by(ordering)
    if offset:
        qs = qs[offset:]
    if limit:
        qs = qs[:limit]

    return {
        'total_count': count,
        'results': qs
    }

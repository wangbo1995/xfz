from haystack import indexes
from .models import News

class NewsIndex(indexes.SearchIndex,indexes.Indexable):
    # 这个text字段可以随便取，但是要和template/search/indexes/news/news_<xxx>.txt对应一致
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return News

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

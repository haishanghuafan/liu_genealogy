"""
刘氏乾正公族谱 - 视图模块
"""
from .core import (
    HomeView,
    GenealogyTreeView,
    SearchView,
    logout_view,
)
from .person import (
    PersonListView,
    PersonDetailView,
    PersonCreateView,
    PersonUpdateView,
    PersonEditView,
)
from .branch import (
    BranchListView,
    BranchDetailView,
    BranchCreateView,
    BranchUpdateView,
)
from .generation import (
    GenerationListView,
    GenerationCreateView,
    GenerationUpdateView,
)
from .record import (
    GenealogyRecordListView,
    GenealogyRecordDetailView,
    RecordCreateView,
    RecordUpdateView,
)
from .auth import (
    RegisterView,
    ProfileView,
    MyFamilyView,
    EditPersonView,
)
from .management import (
    ManagementView,
    UploadMediaView,
)
from .api import (
    FamilyTreeAPIView,
    get_generations,
)

__all__ = [
    'HomeView',
    'GenealogyTreeView',
    'SearchView',
    'logout_view',
    'PersonListView',
    'PersonDetailView',
    'PersonCreateView',
    'PersonUpdateView',
    'PersonEditView',
    'BranchListView',
    'BranchDetailView',
    'BranchCreateView',
    'BranchUpdateView',
    'GenerationListView',
    'GenerationCreateView',
    'GenerationUpdateView',
    'GenealogyRecordListView',
    'GenealogyRecordDetailView',
    'RecordCreateView',
    'RecordUpdateView',
    'RegisterView',
    'ProfileView',
    'MyFamilyView',
    'EditPersonView',
    'ManagementView',
    'UploadMediaView',
    'FamilyTreeAPIView',
    'get_generations',
]

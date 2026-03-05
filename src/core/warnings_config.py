# ValidoAI Warnings Suppression
# Suppress common deprecation warnings that are not actionable

[tool:pytest]
filterwarnings =
    # Suppress pkg_resources deprecation warnings
    ignore::DeprecationWarning:pkg_resources.*
    # Suppress SSL certificate warnings
    ignore::UserWarning:ssl.*
    # Suppress CouchDB warnings
    ignore::UserWarning:couchdb.*
    # Suppress NLTK warnings
    ignore::DeprecationWarning:nltk.*
    # Suppress TensorFlow warnings
    ignore::DeprecationWarning:tensorflow.*
    ignore::UserWarning:tensorflow.*
    # Suppress PyTorch warnings
    ignore::DeprecationWarning:torch.*
    ignore::UserWarning:torch.*
    # Suppress scikit-learn warnings
    ignore::DeprecationWarning:sklearn.*
    ignore::FutureWarning:sklearn.*

# Application-level warnings suppression
import warnings

# Suppress specific deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources.*")
warnings.filterwarnings("ignore", category=UserWarning, module="ssl.*")
warnings.filterwarnings("ignore", category=UserWarning, module="couchdb.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="nltk.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="tensorflow.*")
warnings.filterwarnings("ignore", category=UserWarning, module="tensorflow.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="torch.*")
warnings.filterwarnings("ignore", category=UserWarning, module="torch.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="sklearn.*")
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn.*")

print("✅ Warnings suppression configured")

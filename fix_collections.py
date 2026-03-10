#!/usr/bin/env python3
"""
Fix for collections.Iterable compatibility issue in Python 3.10+
This patch should be applied to wordpress_xmlrpc.compat module
"""

import collections
import collections.abc

# Fix the missing Iterable attribute
if not hasattr(collections, 'Iterable'):
    collections.Iterable = collections.abc.Iterable

if not hasattr(collections, 'Mapping'):
    collections.Mapping = collections.abc.Mapping

if not hasattr(collections, 'Sequence'):
    collections.Sequence = collections.abc.Sequence

print("✅ collections compatibility fix applied successfully!")
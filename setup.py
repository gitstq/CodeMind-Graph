#!/usr/bin/env python3
"""
CodeMind-Graph 安装脚本
"""

from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='codemind-graph',
    version='1.0.0',
    description='代码知识图谱可视化与分析工具 - 将代码库转换为交互式知识图谱',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='gitstq',
    author_email='',
    url='https://github.com/gitstq/CodeMind-Graph',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.8',
    install_requires=[
        # 核心依赖 - 纯Python标准库实现，无外部依赖
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'codemind-graph=codemind_graph.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='code-analysis knowledge-graph visualization static-analysis code-quality',
    project_urls={
        'Bug Reports': 'https://github.com/gitstq/CodeMind-Graph/issues',
        'Source': 'https://github.com/gitstq/CodeMind-Graph',
    },
)

import os
import yaml
from config.path import get_config_path

_config_cache = None

def load_config():
    """配置加载器"""
    global _config_cache
    if _config_cache is not None:
        return _config_cache
    config_path = get_config_path()
    try:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"没有找到配置文件: {config_path}")
        with open(config_path, encoding='utf-8') as f:
            _config_cache = yaml.safe_load(f)
        return _config_cache
    except Exception as e:
        raise
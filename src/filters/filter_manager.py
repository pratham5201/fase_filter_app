"""
Filter Storage and Management Module
Handles saving and loading of filter profiles
"""

import json
import os
from typing import Dict, List
from pathlib import Path


class FilterManager:
    def __init__(self, filters_dir: str = "data/filters"):
        self.filters_dir = Path(filters_dir)
        self.filters_dir.mkdir(parents=True, exist_ok=True)
        self.default_filter_file = self.filters_dir / "default_filter.json"
        self.filters_index_file = self.filters_dir / "filters_index.json"

    def save_filter(self, filter_name: str, filter_profile: Dict) -> str:
        """Save a filter profile to file"""
        filter_file = self.filters_dir / f"{filter_name}.json"
        
        with open(filter_file, 'w') as f:
            json.dump({
                'name': filter_name,
                'profile': filter_profile
            }, f, indent=2)
        
        # Update index
        self._update_index()
        
        return str(filter_file)

    def load_filter(self, filter_name: str) -> Dict:
        """Load a filter profile from file"""
        filter_file = self.filters_dir / f"{filter_name}.json"
        
        if not filter_file.exists():
            raise FileNotFoundError(f"Filter {filter_name} not found")
        
        with open(filter_file, 'r') as f:
            data = json.load(f)
        
        return data['profile']

    def get_all_filters(self) -> List[str]:
        """Get list of all available filters"""
        filters = []
        for file in self.filters_dir.glob("*.json"):
            if file.name != "default_filter.json" and file.name != "filters_index.json":
                filter_name = file.stem
                filters.append(filter_name)
        
        return sorted(filters)

    def set_default_filter(self, filter_name: str) -> None:
        """Set a filter as default"""
        if filter_name:
            filter_file = self.filters_dir / f"{filter_name}.json"
            if not filter_file.exists():
                raise FileNotFoundError(f"Filter {filter_name} not found")
            
            # Save default filter reference
            with open(self.default_filter_file, 'w') as f:
                json.dump({'default_filter': filter_name}, f)
        else:
            # Remove default filter
            if self.default_filter_file.exists():
                self.default_filter_file.unlink()

    def get_default_filter(self) -> str:
        """Get the default filter name, or None if not set"""
        if self.default_filter_file.exists():
            with open(self.default_filter_file, 'r') as f:
                data = json.load(f)
                return data.get('default_filter')
        
        return None

    def delete_filter(self, filter_name: str) -> None:
        """Delete a filter"""
        filter_file = self.filters_dir / f"{filter_name}.json"
        
        if filter_file.exists():
            filter_file.unlink()
            
            # If this was the default filter, remove it
            if self.get_default_filter() == filter_name:
                self.set_default_filter(None)
            
            self._update_index()

    def _update_index(self) -> None:
        """Update the filters index"""
        filters = self.get_all_filters()
        
        with open(self.filters_index_file, 'w') as f:
            json.dump({
                'filters': filters,
                'default': self.get_default_filter()
            }, f, indent=2)

    def get_filter_info(self, filter_name: str) -> Dict:
        """Get metadata about a filter"""
        filter_file = self.filters_dir / f"{filter_name}.json"
        
        if not filter_file.exists():
            return None
        
        file_stats = filter_file.stat()
        
        return {
            'name': filter_name,
            'created': file_stats.st_mtime,
            'size': file_stats.st_size
        }

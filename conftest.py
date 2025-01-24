import toml
import pytest
import logging

log = logging.getLogger(__name__)

py_project_toml = "pyproject.toml"
py_project_data = toml.load(py_project_toml)
marker_groups:dict[str,list[str]] = py_project_data["tool"]["pytest"]["marker_groups"]

#Look through all collected tests and ensure every group is represented
# Currently we do not delete marker groups that are over-selected (more than one member chosen), but that could change
def pytest_collection_modifyitems(session:pytest.Session, config:pytest.Config, items:list[pytest.Item])->None:
    
    for test in items:
        current_markers = [m.name for m in test.own_markers]
        # Investigate for each group to ensure represented
        for mark_group in marker_groups.keys():
            #Investigate each marker
            member_marker_found:bool = False
            for marker in marker_groups[mark_group]:
                if marker in current_markers:
                    member_marker_found = True
                    break
            
            if not member_marker_found:
                default_group_marker:str = marker_groups[mark_group][0]
                test.add_marker(default_group_marker)
                current_markers.append(default_group_marker)
                log.debug(f"Added marker {default_group_marker} of group {mark_group} to test {test.name}")


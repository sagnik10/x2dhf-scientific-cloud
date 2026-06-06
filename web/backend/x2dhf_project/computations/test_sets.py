from pathlib import Path
from django.conf import settings


def test_sets_root():
    configured=Path(settings.X2DHF_DIRECTORY)/'test-sets'
    root=configured if configured.is_absolute() else Path(settings.REPO_ROOT)/'test-sets'
    return root.resolve()


def relative_case_path(path,root=None):
    root=root or test_sets_root()
    return '/'.join(path.resolve().relative_to(root).parts)


def reference_for_input(input_path):
    if input_path.name=='input.data':
        return input_path.with_name('reference.lst')
    return input_path.with_name(input_path.name.replace('input','reference').replace('.data','.lst'))


def case_metadata(path,root=None,include_input=False):
    root=root or test_sets_root()
    parsed=parse_case_input(path.read_text(encoding='utf-8',errors='replace'))
    reference=reference_for_input(path)
    data={
        'name':relative_case_path(path,root),
        'path':relative_case_path(path,root),
        'group':path.parent.parent.name,
        'set':path.parent.name,
        'input_file':path.name,
        'reference_path':relative_case_path(reference,root) if reference.exists() else '',
        'title':parsed.get('title') or relative_case_path(path,root),
        'method':parsed.get('method') or 'hf',
        'summary':parsed.get('summary') or '',
    }
    if include_input:
        data['input']=path.read_text(encoding='utf-8',errors='replace')
    return data


def list_test_cases():
    root=test_sets_root()
    if not root.exists():
        return []
    return [case_metadata(path,root) for path in sorted(root.glob('*/*/input*.data'))]


def read_test_case(case_path):
    root=test_sets_root()
    path=(root/case_path).resolve()
    if not path.is_file() or root not in path.parents:
        raise FileNotFoundError(case_path)
    return case_metadata(path,root,include_input=True)


def parse_case_input(text):
    values={'title':'','method':'','summary':''}
    for raw in text.splitlines():
        line=raw.strip()
        if not line or line.startswith(('#','!')):
            continue
        parts=line.split()
        label=parts[0].lower()
        if label=='title' and len(parts)>1:
            values['title']=' '.join(parts[1:])
        elif label=='method' and len(parts)>1:
            values['method']=parts[1].lower()
        elif label=='nuclei' and len(parts)>3:
            values['summary']=f"ZA {parts[1]}, ZB {parts[2]}, R {parts[3]}"
    return values

import click
import frontmatter
import markdown
from os import cpu_count
from multiprocessing.pool import ThreadPool
from pathlib import Path
from dataclasses import dataclass
from list_all_files_recursively import get_folder_file_complete_path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

@dataclass
class Page:
    dir_path: str
    name: str
    fm: any
    
    def load(info, content):
        with open(info.path) as f:
            fm = frontmatter.load(f)
            html = markdown.markdown(fm.content, extensions=['codehilite', 'fenced_code'])
            fm['content'] = html
            return Page(dir_path=info.folder[len(content) + 1:], name=info.file, fm=fm)


@click.command()
@click.option('--content', type=click.Path(exists=True, dir_okay=True, file_okay=False), default="content", help="content dir path")
@click.option('--layouts', type=click.Path(exists=True, dir_okay=True, file_okay=False), default="layouts", help="layouts dir path")
def build(content, layouts):
    cpus = cpu_count() or 1
    print("CPU count: ", cpus)
    print("Hello from blazingly-fast-python-ssg!")
    files = get_folder_file_complete_path(folders=[content])
    md_paths = [x for x in files if x.ext == '.md']
    pages = [Page.load(x, content) for x in md_paths]
    # with ThreadPool(cpus) as pool: 
    #     pages = pool.map(lambda x: Page.load(x, content), md_paths)
    print(pages)
    
    env = Environment(
        loader=FileSystemLoader(layouts),
        autoescape=select_autoescape()
    )   

    pages.sort(key= lambda p: p.fm['date'], reverse=True)


    public = Path('public')
    public.mkdir(exist_ok=True)
    for i, p in enumerate(pages):
        render_page(env, i, p, public, pages)
        # with ThreadPool(cpus) as pool: 
        #     pool.apply(render_page, (env, i, p, public, pages))
    
        
        

def render_page(env, i, p, public, pages):
    t = env.get_template(p.fm['layout'])
    out_dir = public / p.dir_path
    if p.name != 'index.md':
        out_dir = out_dir / p.name[:len(".md")]
    out_dir.mkdir(exist_ok=True, parents=True)
    out = out_dir / "index.html"

    next = pages[i - 1] if i > 0 else None
    prev = pages[i + 1] if i < len(pages) - 2 else None
    out.write_text(t.render(**p.fm, all_pages=pages, prev=prev, next=next))



    

if __name__ == "__main__":
    build()

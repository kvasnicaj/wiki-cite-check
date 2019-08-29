from flask import Flask, redirect, render_template, url_for

from src.forms import PageForm
from src.link import Link
from src.models import Search, db
from src.wiki import Wiki
from config.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


@app.route('/',)
def index():
    '''Homepage with search form.'''
    form = PageForm()
    return render_template('index.html', form=form)


@app.route('/result', methods=['GET', 'POST'])
def result():
    ''' First ten results right after submitting the form '''
    form = PageForm()

    if form.validate_on_submit():
        wp = Wiki(form.page.data)
        rows = []

        num = len(wp.wikipage.references)
        end = 10 if num > 10 else num

        # log form to db
        db.session.add(Search(numLinks=num,
                              keyword=form.page.data,
                              ))
        db.session.commit()

        for index in range(0, end):
            link = Link(wp.wikipage.references[index])
            rows.append(link.isLive())

        return render_template('results.html',
                               desc=wp.getDescription(),
                               rows=rows,
                               page=0,
                               limit=Config.ROW_LIMIT,
                               max=len(wp.wikipage.references))
    else:
        return redirect(url_for('noresult'))


@app.route('/results/<name>/<page>')
def results(name, page):
    ''' Results for the next pages that come without a form
    but with GET parametrs'''
    wp = Wiki(name)
    rows = []

    start = Config.ROW_LIMIT * int(page)
    end = start + Config.ROW_LIMIT

    if len(wp.wikipage.references) < end:
        end = len(wp.wikipage.references)

    for index in range(start, end):
        link = Link(wp.wikipage.references[index])
        rows.append(link.isLive())

    return render_template('results.html',
                           desc=wp.getDescription(),
                           rows=rows,
                           page=int(page),
                           limit=Config.ROW_LIMIT,
                           max=len(wp.wikipage.references))


@app.route('/noresult')
def noresult():
    return render_template('errors/noresult.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


if __name__ == '__main__':
    app.run()

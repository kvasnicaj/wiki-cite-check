from flask import Flask, render_template

from src.forms import PageForm
from src.link import Link
from src.models import Search, LinksLog, db, logSearch
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


@app.route('/results', methods=['GET', 'POST'], defaults={'page': 0,
                                                          'name': 'submit'})
@app.route('/results/<name>/<int:page>')
def results(name, page):
    ''' First ten results right after submitting the form
    and thne for the next pages come without a form
    but with GET parametrs'''
    form = PageForm()

    if form.validate_on_submit():
        wp = Wiki(form.page.data)
        start = 0

        try:
            num = len(wp.wikipage.references)
        except KeyError:
            logSearch(form.page.data, 0)
            return render_template('errors/noresult.html',
                                   message='Stránka nemá žádné reference.')
        except AttributeError:
            logSearch(form.page.data, -1)
            return render_template('errors/noresult.html',
                                   message='Tato stránka neexistuje.')

        logSearch(form.page.data, num)
        end = 10 if num > 10 else num

    else:
        wp = Wiki(name)

        try:
            num = len(wp.wikipage.references)
        except AttributeError:
            return render_template('errors/noresult.html',
                                   message='Tato stránka neexistuje.')

        start = Config.ROW_LIMIT * int(page)
        end = start + Config.ROW_LIMIT

        if num < end:
            end = num

    rows = []
    for index in range(start, end):
        link = Link(wp.wikipage.references[index])
        result = link.isLive()
        rows.append(result)

        # log result to db
        db.session.add(LinksLog(url=result.link,
                                status=result.status_code,
                                wal=result.sign))
        db.session.commit()

    return render_template('results.html',
                           desc=wp.getDescription(),
                           rows=rows,
                           page=int(page),
                           limit=Config.ROW_LIMIT,
                           max=len(wp.wikipage.references))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


if __name__ == '__main__':
    app.run()

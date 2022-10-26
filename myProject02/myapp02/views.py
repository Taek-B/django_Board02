from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from myapp02.models import Board, Comment
import math
import urllib.parse
from django.core.paginator import Paginator

# Create your views here.

UPLOAD_DIR = 'C:/Django_practice/upload/'


# index
def base(request):
    return render(request, 'base.html')


# write_form
def write_form(request):
    return render(request, 'board/insert.html')


# insert
@csrf_exempt
def insert(request):
    fname = ''
    fsize = 0

    if 'file' in request.FILES:
        file = request.FILES['file']
        fname = file.name
        fsize = file.size

        fp = open('%s%s' % (UPLOAD_DIR, fname), 'wb')
        for chunk in file.chunks():
            fp.write(chunk)
        fp.close()

    dto = Board(writer=request.POST['writer'],
                title=request.POST['title'],
                content=request.POST['content'],
                filename=fname,
                filesize=fsize
                )
    dto.save()
    return redirect('/')


# list
def list(request):
    page = request.GET.get('page', 1)
    word = request.GET.get('word', '')
    field = request.GET.get('field', 'title')

    # 페이지 번호 설정
    # boardCount
    if field == 'all':
        # Q
        # '__' : like랑 같다
        boardCount = Board.objects.filter(Q(writer__contains=word) |
                                          Q(title__contains=word) |
                                          Q(content__contains=word)).count()
    elif field == 'writer':
        boardCount = Board.objects.filter(
            Q(writer__contains=word)).count()
    elif field == 'title':
        boardCount = Board.objects.filter(
            Q(title__contains=word)).count()
    elif field == 'content':
        boardCount = Board.objects.filter(
            Q(content__contains=word)).count()
    else:
        boardCount = Board.objects.all().count()

    pageSize = 5    # 한 화면 게시글 수
    blockPage = 3   # 보이는 페이지 수
    currentPage = int(page)

    # 시작위치?
    start = (currentPage-1)*pageSize
    totPage = math.ceil(boardCount / pageSize)  # 전체페이지 // ceil : 올림
    startPage = math.floor((currentPage - 1)/blockPage) * \
        blockPage + 1   # floor : 버림
    endPage = startPage + blockPage - 1
    # 게시글의 전체 페이지 수 = math.ceil(게시글 수 / pageSize)

    # 마지막 페이지가 총 페이지 수 보다 클 때 마지막 페이지는 총 페이지 수의 값을 받음
    if endPage > totPage:
        endPage = totPage

    # 검색
    if field == 'all':
        boardList = Board.objects.filter(Q(writer__contains=word) |
                                         Q(title__contains=word) |
                                         Q(content__contains=word)).order_by('-id')[start: start + pageSize]
    elif field == 'writer':
        boardList = Board.objects.filter(
            Q(writer__contains=word)).order_by('-id')[start: start + pageSize]
    elif field == 'title':
        boardList = Board.objects.filter(
            Q(title__contains=word)).order_by('-id')[start: start + pageSize]
    elif field == 'content':
        boardList = Board.objects.filter(
            Q(content__contains=word)).order_by('-id')[start: start + pageSize]
    else:
        boardList = Board.objects.all().order_by(
            '-id')[start: start + pageSize]

    # dict형태
    context = {'boardList': boardList,
               'startPage': startPage,
               'blockPage': blockPage,
               'endPage': endPage,
               'totPage': totPage,
               'boardCount': boardCount,
               'currentPage': currentPage,
               'field': field,
               'word': word,
               'range': range(startPage, endPage+1)}
    return render(request, 'board/list.html', context)


# 다운로드 횟수
def download_count(request):
    id = request.GET['id']
    dto = Board.objects.get(id=id)
    dto.down_up()
    dto.save()
    count = dto.down
    # Spring에 있는 responsebody랑 같다
    # 데이터 값을 받기 위해 !!
    return JsonResponse({'id': id, 'count': count})


# 다운로드
def download(request):
    id = request.GET['id']
    dto = Board.objects.get(id=id)
    path = UPLOAD_DIR + dto.filename

    filename = urllib.parse.quote(dto.filename)
    # print('filename : ', filename)
    with open(path, 'rb') as file:
        response = HttpResponse(file.read(),
                                content_type='application/octet-stream')
        response['Content-Disposition'] = "attachment;filename*=UTF-8 '' {0}".format(
            filename)
    return response


# list_page
def list_page(request):
    page = request.GET.get('page', 1)
    word = request.GET.get('word', '')

    boardCount = Board.objects.filter(Q(writer__contains=word) |
                                      Q(title__contains=word) |
                                      Q(content__contains=word)).count()

    boardList = Board.objects.filter(Q(writer__contains=word) |
                                     Q(title__contains=word) |
                                     Q(content__contains=word)).order_by('-id')

    pageSize = 5

    # 페이징처리
    paginator = Paginator(boardList, pageSize)  # import
    page_obj = paginator.get_page(page)
    print('boardCount : ', boardCount)

    context = {'page_list': page_obj,
               'page': page,
               'word': word,
               'boardCount': boardCount}
    return render(request, 'board/list_page.html', context)


# detail
def detail(request, board_id):
    dto = Board.objects.get(id=board_id)
    dto.hit_up()
    dto.save()
    return render(request, 'board/detail.html', {'dto': dto})

# DaeguSubway-tkinter
Tkinter로 구성한 대구 도시철도 시간표 표시 프로그램

![메인 화면](https://user-images.githubusercontent.com/60684821/191521610-b56a08da-2268-42cd-b008-ac932b4cc5c6.png)
![역사별 시간표](https://user-images.githubusercontent.com/60684821/191521860-d7fb9ee6-b67f-4c9f-b0f2-62d611ea470a.png)
![열차별 시간표](https://user-images.githubusercontent.com/60684821/191521873-5cd1f9b5-4238-49b6-9823-ff42602b1827.png)


# 특징
  1. 첫 시작시 시간표, 휴일 정보를 인터넷에서 받아옵니다. (시간표: 공공데이터 포털 / 휴일 정보: 네이버)
  2. 대기상태에서 자동으로 열차 시간이 새로고침 됩니다.
  3. 기차가 마지막 역까지 운행하지 않을 경우 목적지를 표시합니다.
  4. 열차번호별 시간표를 제공합니다. 이를 통해 자세한 출발 시각을 알 수 있습니다.
  5. 파이썬 표준 라이브러리만을 사용하였습니다.
  6. 대기상태에서 CPU 점유율이 높지 않습니다.

# 실행 방법
### 파이썬 파일을 통한 실행
  1. Repository의 *.py와 *.pyw 파일을 모두 다운로드
  2. MainWindow.pyw 실행
  
### Pyinstaller파일을 통한 실행
  1. https://github.com/eeshin-kr/DaeguSubway-tkinter/releases 에서 *pyinstller.zip 파일 다운로드
  2. *pyinstaller.zip 파일 압축해제
  3. MainWindow.exe 실행

# 사용한 파일
* EXE파일 로고 사진: https://en.wikipedia.org/wiki/File:Aiga_railtransportation_25.svg
* EXE파일 로고 폰트: 나눔바른고딕


var month_olypic = [31,29,31,30,31,30,31,31,30,31,30,31];//闰年每个月份的天数
var month_normal = [31,28,31,30,31,30,31,31,30,31,30,31];
var month_name =["一月","二月","三月","四月","五月","六月","七月","八月","九月","十月","十一月","十二月"];

var my_date = new Date();
var my_year = my_date.getFullYear();
var my_month = my_date.getMonth();
var my_day = my_date.getDate();

//获取以上各个部分的id
var holder = document.getElementById("days");
var prev = document.getElementById("prev");
var next = document.getElementById("next");
var ctitle = document.getElementById("calendar-title");
var cyear = document.getElementById("calendar-year");

// 获取隐藏模块对象
var modal = document.getElementById("myBorrowInfo");

// 获取设备id
var instrument_id = document.getElementById("instrument_id").innerHTML;

// 初始化选择状态
var now_choose = 'intermittent';
document.getElementById("intermittent").click();

// 数据库已有的时间
var OcontinueTime = Array();
var OintermittentTime = Array();

// 现在添加的信息
var continueTime = Array();
var intermittentTime = Array();

//
var ClickBool = false;

//根据年月获取当月第一天是周几
function dayStart(month,year){
    var tmpDate = new Date(year, month, 1);
    return (tmpDate.getDay());
}
//根据年份判断某月有多少天(11,2018),表示2018年12月
function daysMonth(month, year){
    var tmp1 = year % 4;
    var tmp2 = year % 100;
    var tmp3 = year % 400;

    if((tmp1 == 0 && tmp2 != 0) || (tmp3 == 0)){
        return (month_olypic[month]);//闰年
    }else{
        return (month_normal[month]);//非闰年
    }
}

// 判断日期状态
function judgedState(DateStr){
    if(OcontinueTime.length > 0){
        for(var i = 0; i<OcontinueTime.length; i++){
            if(parseInt(OcontinueTime[i][0]) <= parseInt(DateStr) && parseInt(OcontinueTime[i][1]) >= parseInt(DateStr)){
                myclass = "class = 'continue lightgrey'";
                return myclass;
            }
        }
    }
    if(OintermittentTime.length > 0){
        for(var i = 0; i<OintermittentTime.length; i++){
            if(parseInt(OintermittentTime[i][0]) <= parseInt(DateStr) && parseInt(OintermittentTime[i][1]) >= parseInt(DateStr)){
                myclass = "class = 'intermittent lightgrey'";
                return myclass;
            }
        }
    }
    
    // 当前选择
    if(continueTime[0] <= parseInt(DateStr) && parseInt(continueTime[1]) >= parseInt(DateStr)){
        myclass = "class = 'continue lightgrey'";
        return myclass;
    }else if(intermittentTime[0] <= parseInt(DateStr) && intermittentTime[1] >= parseInt(DateStr)){
        myclass = "class = 'intermittent lightgrey'";
        return myclass;
    }   else{
        myclass = "class = 'darkgrey'";
        return myclass;
    }


}

// 日历点击事件
days_ul = document.getElementById('days');
days_ul.onclick = function(){
    lis = document.getElementsByTagName("li");
    console.log('click')
    for(var i = 0; i<lis.length; i++){

        (function(n){
            lis[i].onclick = function(){
                if(parseInt(lis[n].innerHTML) < 10){
                    dataStr = my_year.toString()+(my_month+1).toString()+'0' + lis[n].innerHTML;
                }else{
                    dataStr = my_year.toString()+(my_month+1).toString()+lis[n].innerHTML;
                }
                lis[n].className = judgedClickDate(lis[n].className, dataStr);
            }
        })(i)
    }
}

function refreshDate() {
    var str = "";
    var totalDay = daysMonth(my_month, my_year);
    var firstDay = dayStart(my_month, my_year);

    for(var i = 0; i<firstDay; i++){
        str += "<li>" + "</li>";
    }

    var myclass;
    for(var i = 1; i<= totalDay; i++){
        if(i < 10){
            dataStr = my_year.toString()+(my_month+1).toString()+'0' + i;
        }else{
            dataStr = my_year.toString()+(my_month+1).toString()+i;
        }

        //console.log(dataStr);
        if((my_year < my_date.getFullYear())||(my_year == my_date.getFullYear() && my_month < my_date.getMonth()) || (my_year == my_date.getFullYear() && my_month == my_date.getMonth() && i < my_day)){
            myclass = " class='lightgrey'";
        } else {
            myclass = judgedState(dataStr);
        }
        str += "<li "+myclass+">"+i+"</li>";
    }
    holder.innerHTML = str;
    ctitle.innerHTML = month_name[my_month];
    cyear.innerHTML = my_year;

    days_ul.click();
}

pre.onclick = function(e){
    e.preventDefault();
    my_month--;
    if(my_month < 0){
        my_year--;
        my_month = 11; //即12月份
    }
    refreshDate();
}

next.onclick = function(e){
    e.preventDefault();
    my_month++;
    if(my_month > 11){
        my_month = 0;
        my_year++;
    }
    refreshDate();
}

refreshDate();

// 删除日期
function deleteArrayDataIndex(dataStr, Array) {
    var index = Array.indexOf(dataStr);
    if (index > -1) {
        Array.splice(index, 1)
    }
}

// 点击日期判断
function judgedClickDate(className, getDataStr){
    // 过去不可选和已选挂测
    if (className == 'lightgrey' || className == 'continue lightgrey') {
        displayModal();
        console.log("displayModal");
    }
    // 过去调试
    else if(className == 'intermittent lightgrey'){
        className = 'intermittent darkgrey';
    }else{
        if(now_choose == 'continue'){
            if(!ClickBool){
                continueTime[0] = parseInt(getDataStr);
                className = 'continue';
                ClickBool = true;
            }else{
                continueTime[1] = parseInt(getDataStr);
                refreshDate();
                ClickBool = false;
            }
        }else{
            if(!ClickBool){
                intermittentTime[0] = parseInt(getDataStr);
                className = 'intermittent';
                ClickBool = true;
            }else{
                intermittentTime[1] = parseInt(getDataStr);
                refreshDate();
                ClickBool = false;
            }
        }
    }
    return className;
}




// ====================== 切换当前选择状态 ============================
var radio_continue = document.getElementById("continue");
radio_continue.onclick=function(e){
    now_choose = "continue";
}

var radio_intermittent = document.getElementById('intermittent');
radio_intermittent.onclick=function(e){
    now_choose = "intermittent";
}

var radio_intermittent = document.getElementById('free');
radio_intermittent.onclick=function(e){
    now_choose = "free";
    intermittentTime = [];
    continueTime = [];
    refreshDate();
}

// ======================= ajax ============================
// 显示弹窗
function displayModal() {
    modal.style.display = "block";
}

$(function(){
    initData();
});

// 获取数据
function initData(){
    $.ajax({
        type:'GET',
        dataType: "json",
        url:"/instrument/getBorrowTime/" + instrument_id,
        success: function (data){
            console.log(data);
            for(var i = 0; i<data['continue'].length; i++){
                OcontinueTime[i] = data['continue'][i];
            }

            for(var i = 0; i<data['intermittent'].length; i++){
                OintermittentTime[i] = data['intermittent'][i];
            }
            console.log(OcontinueTime)
            refreshDate()
        },
        error:function(){alert("数据请求失败");}
    })
}

function putBorrowTime(){

    // 检测数据是否合法
    if((continueTime[0] <= continueTime[1]) || (intermittentTime[0] <= intermittentTime[1])){
        // 需要上传的json数据，调用JSON.stringify进行转换
        var datas= {
            timeData: JSON.stringify({
                'continueTime': continueTime,
                'intermittentTime': intermittentTime
            }),
        }
        console.log(datas);
        $.ajax({          
            url:"/instrument/putBorrowTime/" + instrument_id, 
            type:'POST',
            dataType:"text",  
            data: datas,
            success:function(data){
                if(data == 'None'){
                    alert('提交数据不合法');
                }else{
                    alert('提交成功，点击刷新');
                    location.reload();
                }
            },      
            error:function(XMLHttpRequest, textStatus, errorThrown){
                alert('数据提交失败');
            }
        });
    }else{
        intermittentTime = [];
        continueTime = [];
        refreshDate();
    }
}

function deteleBorrowTime(){
    var r=confirm("确定删除借用信息吗？");
    if(r == true){
        // 删除该仪器下已有的租借信息
        $.ajax({ 
            url:"/instrument/deleteBorrowTime/" + instrument_id, 
            type:'GET',
            dataType:"text",  
            success:function(data){
                if(data == 'success'){
                    alert('删除成功，点击刷新');
                    location.reload();
                }
            },
            error:function(XMLHttpRequest, textStatus, errorThrown){
                alert('删除失败');
            }
        })
    }
}

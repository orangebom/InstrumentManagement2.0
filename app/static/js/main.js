function indexSearch() {
    // 声明变量
    var input, filter, table, tr, td, i;
    input = document.getElementById("indexInput");
    filter = input.value.toUpperCase();
    table = document.getElementById("indexTable");
    tr = table.getElementsByTagName("tr");
  
    // 循环表格每一行，查找匹配项
    for (i = 0; i < tr.length; i++) {
      td = tr[i].getElementsByTagName("td")[1];
      if (td) {
        if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
          tr[i].style.display = "";
        } else {
          tr[i].style.display = "none";
        }
      }
    }
  }


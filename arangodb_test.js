var n = 1000;
var cn = "testdocs_js";
db._drop(cn);
SYS_WAIT(4);
db._create(cn);
SYS_WAIT(3);

var c = db._collection(cn);
var t = SYS_TIME();

for (var i = 0; i < n; ++i) {
    c.save({ "value" : "test_" + i });
}

print(SYS_TIME() - t);
print(c.count());
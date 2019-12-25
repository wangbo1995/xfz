var gulp = require('gulp'),
    cssnano = require('gulp-cssnano'),
    sass = require('gulp-sass'),
    rename = require('gulp-rename'),
    uglify = require('gulp-uglify'),
    concat = require('gulp-concat'),
    cache = require('gulp-cache'),
    imagemin = require('gulp-imagemin'),
    // 这个插件有个方法log，可以打印出当前js错误的信息,而不是直接退出gulp
    util = require('gulp-util'),
    // 这个插件是运行时js代码报错，因为js被压缩都在一行，浏览器console不
    // 好定位错误，这个插件可以追踪到原始js文件报错的行数
    sourcemaps = require('gulp-sourcemaps'),
    bs = require('browser-sync').create();

var path = {
    //注意**代表中间可以有任意多个目录
    'html': './templates/**/',
    'css': './src/css/**/',
    'js': './src/js/',
    'images': './src/images/',
    'css_dist': './dist/css/',
    'js_dist': './dist/js/',
    'images_dist': './dist/images/',
};
// 定义一个处理html文件的任务
gulp.task('html', function () {
    gulp.src(path.html + '*.html')
        .pipe(bs.stream())
});
//定义一个处理css文件的任务
gulp.task('css', function () {
    gulp.src(path.css + '*.scss')
        //使用sass写css，并讲scss文件解析成css，注意要打开logError
        .pipe(sass().on('error', sass.logError))
        .pipe(cssnano())
        .pipe(rename({'suffix': '.min'}))
        .pipe(gulp.dest(path.css_dist))
        .pipe(bs.stream())
});
// 定义一个处理js文件的任务
gulp.task('js', function () {
    gulp.src(path.js + '*.js')
        .pipe(sourcemaps.init())
        // .pipe(concat('index.js'))
        .pipe(uglify().on('error', util.log))
        .pipe(rename({'suffix': '.min'}))
        .pipe(sourcemaps.write())
        .pipe(gulp.dest(path.js_dist))
        .pipe(bs.stream())
});
// 定义一个处理图片文件的任务
gulp.task('images', function () {
    gulp.src(path.images + '*.*')
        .pipe(cache(imagemin()))
        .pipe(gulp.dest(path.images_dist))
        .pipe(bs.stream())
});
// 定义一个监听文件修改的任务
gulp.task('watch', function () {
    gulp.watch(path.html + '*.html', ['html']);
    gulp.watch(path.css + '*.scss', ['css']);
    gulp.watch(path.js + '*.js', ['js']);
    gulp.watch(path.images + '*.*', ['images'])
});
// 初始化browser-sync的任务
gulp.task('bs', function () {
    bs.init({
        'server': {
            baseDir: './'
        }
    })
});
// 创建启动浏览器监听任务
// gulp.task('default', ['bs', 'watch']);
// 写后端项目，是用Django启动的不需要browser-sync给我们起3000端口的那个服务
gulp.task('default', ['watch']);

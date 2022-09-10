const menu3 = document.querySelector('.mmm');
const toggle = document.querySelector('.toggle');
const bar = document.querySelector('.bar');
const close = document.querySelector('.close');
const cls = document.querySelector('.cls');
const btnn = document.querySelector('.btnn');
const btnn1 = document.querySelector('.btnn1');
const btnn2 = document.querySelector('.btnn2');
const btnn3 = document.querySelector('.btnn3');
const pk = document.querySelector('.package-wraper');
const extra = document.querySelector('.extra');


const mn = document.querySelector('.mn');
const an = document.querySelector('.an');
const custom = document.querySelector('.custom');

const m = document.getElementById('m');
const a = document.getElementById('a');
const l = document.getElementById('l');
const usd = document.querySelector('.usd');

m.addEventListener('click', () => {
    usd.innerHTML = "3";
    m.classList.add('btn-click');
    a.classList.remove('btn-click');
    l.classList.remove('btn-click');
    mn.style.display = "block"
    an.style.display = "block"
    custom.style.display = "block"
    pk.style = "grid-gap:3em"
    an.style = "grid-template-columns:1fr;"
    extra.classList.remove('actv')

});
a.addEventListener('click', () => {
    usd.innerHTML = "30";
    m.classList.remove('btn-click');
    a.classList.add('btn-click');
    l.classList.remove('btn-click');
    pk.style.display = "none"
    mn.style.display = "none"
    extra.classList.add('actv')
});
l.addEventListener('click', () => {
    usd.innerHTML = "500";
    m.classList.remove('btn-click');
    a.classList.remove('btn-click');
    l.classList.add('btn-click');
    pk.style = "grid-gap:0"
    an.style = "grid-column:2/2;"
    extra.classList.remove('actv')


    mn.style.display = "none"
    an.style.display = "block"
    custom.style.display = "none"
});

bar.addEventListener('click', () => {
    close.style.display = "block";
    bar.style.display = "none";
});
cls.addEventListener('click', () => {
    close.style.display = "none";
    bar.style.display = "block";
});

function my() {
    menu3.classList.toggle('active');
}
btnn.addEventListener('click', () => {
    close.style.display = "none";
    bar.style.display = "block";
    menu3.classList.toggle('active');
});

btnn1.addEventListener('click', () => {
    close.style.display = "none";
    bar.style.display = "block";
    menu3.classList.toggle('active');
});


btnn2.addEventListener('click', () => {
    close.style.display = "none";
    bar.style.display = "block";
    menu3.classList.toggle('active');
});
btnn3.addEventListener('click', () => {
    close.style.display = "none";
    bar.style.display = "block";
    menu3.classList.toggle('active');
});




from pathlib import Path
root=Path(__file__).resolve().parents[3]
test=root/'tests/team/java/com/bookflow/team'
reg=test/'StateRegressionTest.java'
s=reg.read_text();methods=s[s.index(' @Test void lost'):s.rfind('}')]
p=test/'IssueReturnTest.java';s=p.read_text();p.write_text(s[:s.rfind('}')]+methods+'\n}\n');reg.unlink()
p=root/'src/main/java/com/bookflow/service/IssueReturnService.java';s=p.read_text();s=s.replace('        LocalDate issueDate = LocalDate.now();','''        if (transactionRepository.findByMemberSystemIdAndBookIsbnAndStatus(
                member.getSystemId(), book.getIsbn(), Transaction.TxnStatus.ISSUED).isPresent()) {
            throw new BookFlowException("Member already has an active loan for this book");
        }

        LocalDate issueDate = LocalDate.now();''');s=s.replace('if (txn.getStatus() == Transaction.TxnStatus.RETURNED)', 'if (txn.getStatus() != Transaction.TxnStatus.ISSUED)').replace('This book has already been returned','Only issued books can be returned; this transaction is already closed')
p.write_text(s)
